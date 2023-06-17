
#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴ 
 
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

import random
import feedparser
import aiohttp
import os

from hikkatl.types import Message
from .. import loader, utils
from ..inline.types import InlineCall, InlineQuery

@loader.tds
class MusicModule(loader.Module):
    """Module for music for programming from https://musicforprogramming.net/"""
    strings = {
        "name": "ProgMusic",
        "fetching": "<b>Fetching music...</b>",
        "downloading": "<b>Downloading... Please wait, usually it takes in 3-7 minutes ❤️</b>",
        "download_failed": "<b>Failed to download music.</b>",
        "successful": "<b>Enjoy the music!</b>"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(en_doc="send random chill music")
    async def prmusic(self, m: Message):
        """Send music for programming"""
        await m.edit(self.strings["fetching"])

        # загрузка и разбор RSS-канала
        rss_url = "https://musicforprogramming.net/rss.xml"
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            await m.edit("Failed to fetch music.")
            return

        # выбор любого айтема
        random_entry = random.choice(feed.entries)

        # получение информации
        title = random_entry.title
        description = random_entry.description
        link = random_entry.link
        download_url = random_entry.enclosures[0].href

        if not download_url:
            await m.edit("Failed to fetch music.")
            return

        # Отправка информации и кнопки скачивания
        chat_id = m.chat_id
        form_message = await self.inline.form(
            text=f"<b>{title}</b>\n\n<b>Description:</b> {description}",
            message=m,
            reply_markup=[
                [{"text": "Link 🔗", "url": link}],
                [{"text": "Download ⬇️", "callback": lambda c, u=download_url, l=link, t=title: self.download_and_send_music(c, m.chat_id, u, t, l)}],
                [{"text": "Close ❌", "callback": self.close}],
            ],
            silent=True
        )

    async def close(self, call):
        """Close the inline form"""
        await call.delete()

    async def download_and_send_music(self, call, chat_id, download_url, title, link):
        await call.edit(text= f"<b>Title: {title}</b>\n<b>Link: {link}</b>\n\n" + self.strings["downloading"])
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    return

                file = await response.read()

        # определение расширения файла
        extension = download_url.split(".")[-1]

        # сохранение временного файла
        temp_file_path = os.path.join(os.getcwd(), f"chill.{extension}")
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file)

        # отправка музыки
        await self.client.send_file(chat_id, temp_file_path, voice = True, only_document=False, caption=self.strings["successful"] + f"\n\n<b>Title: {title}</b>\n<b>Link: {link}</b>" )

        # удаление временного файла
        os.remove(temp_file_path)
        await call.delete()

