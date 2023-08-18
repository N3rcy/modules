#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

from hikkatl.tl.types import Message

from .. import loader, utils


@loader.tds
class WatcherModule(loader.Module):
    """Module for watching and responding to specific words"""

    strings = {
        "name": "WatcherModule",
        "watch_added": (
            "<emoji document_id=5210956306952758910>👀</emoji>Watch added: {word}"
        ),
        "watch_removed": (
            "<b><emoji document_id=5980930633298350051>✅</emoji>Watch removed:</b>"
            " {word}"
        ),
        "watch_list": (
            "<b><emoji document_id=5818865088970362886>❕</emoji>List of watched"
            " words:</b>\n\n{watch_list}"
        ),
    }

    strings_ru = {
        "watch_added": (
            "<b><emoji document_id=5210956306952758910>👀</emoji>Отслеживание"
            " добавлено:</b> {word}"
        ),
        "watch_removed": (
            "<b><emoji document_id=5980930633298350051>✅</emoji>Отслеживание"
            " удалено:</b> {word}"
        ),
        "watch_list": (
            "<b><emoji document_id=5818865088970362886>❕</emoji>Список отслеживаемых"
            " слов:</b>\n\n{watch_list}"
        ),
    }

    def __init__(self):
        self._watches = {}

    async def client_ready(self):
        self._load_watches()

    async def watcher(self, message: Message):
        """Watcher method to track and respond to specific words"""
        if getattr(message, "text", None):
            text = message.text.lower()
            for word, response in self._watches.items():
                if word.lower() == text:
                    await message.reply(response)

    @loader.command(ru_doc="Добавить отслеживание слова")
    async def addwatch(self, message: Message):
        """Add a word to be watched"""
        if len(args := utils.get_args_split_by(message, "$")) < 2:
            await utils.answer(
                message,
                (
                    "<emoji document_id=5978859389614821335>❌</emoji> Не указан один"
                    ' из аргументов! Пример правильной команды: `.addwatch "первое'
                    ' слово"$"ответ на него"`'
                ),
            )
            return

        word = args[0].strip()
        response = args[1].strip()
        self._watches[word] = response
        self._save_watches()
        await utils.answer(message, self.strings("watch_added").format(word=word))

    @loader.command(ru_doc="Удалить отслеживание слова")
    async def rmwatch(self, m: Message):
        """Remove a word from being watched"""
        if (word := utils.get_args_raw(m)) not in self._watches:
            await utils.answer(m, f"Watch not found for word: {word}")
            return

        del self._watches[word]
        self._save_watches()
        await utils.answer(m, self.strings("watch_removed").format(word=word))

    @loader.command(ru_doc="Показать список отслеживаемых слов")
    async def listwatches(self, message: Message):
        """Show the list of watched words"""
        if not self._watches:
            await utils.answer(message, "No watches found")
            return

        await utils.answer(
            message,
            self.strings("watch_list").format(
                watch_list="\n".join(
                    f"{word}: {response}" for word, response in self._watches.items()
                )
            ),
        )

    def _save_watches(self):
        self.set("watches", self._watches)

    def _load_watches(self):
        self._watches = self.get("watches", {})
