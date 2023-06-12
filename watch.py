
#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴ 
 
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

from hikkatl.types import Message
from telethon import events
from .. import loader, utils


@loader.tds
class WatcherModule(loader.Module):
    """Module for watching and responding to specific words"""
    strings = {"name": "WatcherModule",
    "watch_added": "<emoji document_id=5210956306952758910>👀</emoji>Watch added: {word}",
    "watch_removed": "<b><emoji document_id=5980930633298350051>✅</emoji>Watch removed:</b> {word}",
    "watch_list": "<b><emoji document_id=5818865088970362886>❕</emoji>List of watched words:</b>\n\n{watch_list}"
    }

    strings_ru = {"watch_added": "<b><emoji document_id=5210956306952758910>👀</emoji>Отслеживание добавлено:</b> {word}",
    "watch_removed": "<b><emoji document_id=5980930633298350051>✅</emoji>Отслеживание удалено:</b> {word}",
    "watch_list": "<b><emoji document_id=5818865088970362886>❕</emoji>Список отслеживаемых слов:</b>\n\n{watch_list}"
    }
    watches = {}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self._load_watches()

    async def watcher(self, message: Message):
        """Watcher method to track and respond to specific words"""
        if message.text:
            text = message.text.lower()
            for word, response in self.watches.items():
                if word in text:
                    await message.reply(response)

    @loader.command(ru_doc="Добавить отслеживание слова")
    async def addwatch(self, m: Message):
        """Add a word to be watched"""
        args = utils.get_args_split_by(m, ",")
        if len(args) < 2:
            await utils.answer(
                m,
                "<emoji document_id=5978859389614821335>❌</emoji> Не указан один из аргументов! Пример правильной команды: `.addwatch \"первое слово\", \"ответ на него\"`"
            )
            return

        word = args[0].strip()
        response = args[1].strip()
        self.watches[word] = response
        self._save_watches()
        await utils.answer(m, self.strings["watch_added"].format(word=word))

    @loader.command(ru_doc="Удалить отслеживание слова")
    async def rmwatch(self, m: Message):
        """Remove a word from being watched"""
        word = utils.get_args_raw(m)
        if word in self.watches:
            del self.watches[word]
            self._save_watches()
            await utils.answer(m, self.strings["watch_removed"].format(word=word))
        else:
            await utils.answer(m, f"Watch not found for word: {word}")

    @loader.command(ru_doc="Показать список отслеживаемых слов")
    async def listwatches(self, m: Message):
        """Show the list of watched words"""
        if self.watches:
            watch_list = "\n".join(f"{word}: {response}" for word, response in self.watches.items())
            await utils.answer(m, self.strings["watch_list"].format(watch_list=watch_list))
        else:
            await utils.answer(m, "No watches found")

    def _save_watches(self):
        self.db.set("WatcherModule", "watches", self.watches)

    def _load_watches(self):
        self.watches = self.db.get("WatcherModule", "watches", {})

    async def client_started(self, client, db):
        self.db = db
        self.client = client
        self.client.add_event_handler(self._handle_message, events.NewMessage())

    async def _handle_message(self, event):
        if isinstance(event.message, Message):
            await self.watcher(event.message)
