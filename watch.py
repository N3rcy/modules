
#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴ 
 
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class WatcherModule(loader.Module):
    """Module for watching and responding to specific words"""
    strings = {"name": "WatcherModule", "watch_added": "Watch added: {word}", "watch_removed": "Watch removed: {word}"}
    strings_ru = {"watch_added": "Отслеживание добавлено: {word}", "watch_removed": "Отслеживание удалено: {word}"}
    watches = {}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def watcher(self, message: Message):
        """Watcher method to track and respond to specific words"""
        if message.text:
            text = message.text.lower()
            for word, response in self.watches.items():
                if word in text:
                    await message.respond(response)

    @loader.command(ru_doc="Добавить отслеживание слова")
    async def addwatch(self, m: Message):
        """Add a word to be watched"""
        args = utils.get_args_split_by(m, ",")
        if len(args) != 2:
            await utils.answer(m, self.strings["watch_added"])
            return

        word = args[0].strip()
        response = args[1].strip()
        self.watches[word] = response
        await utils.answer(m, self.strings["watch_added"].format(word=word))

    @loader.command(ru_doc="Удалить отслеживание слова")
    async def rmwatch(self, m: Message):
        """Remove a word from being watched"""
        word = utils.get_args_raw(m)
        if word in self.watches:
            del self.watches[word]
            await utils.answer(m, self.strings["watch_removed"].format(word=word))
        else:
            await utils.answer(m, f"Watch not found for word: {word}")
