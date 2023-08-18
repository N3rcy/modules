#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

import os
import random

import aiohttp
import feedparser
from hikkatl.tl.types import Message

from .. import loader, utils
from ..inline.types import InlineCall


@loader.tds
class MusicModule(loader.Module):
    """Module for music for programming from https://musicforprogramming.net/"""

    strings = {
        "name": "ProgMusic",
        "fetching": "<b>Fetching music...</b>",
        "downloading": (
            "<b>Downloading... Please wait, usually it takes in 3-7 minutes ❤️</b>"
        ),
        "download_failed": "<b>Failed to download music.</b>",
        "successful": "<b>Enjoy the music!</b>",
    }

    @loader.command(en_doc="send random chill music")
    async def prmusic(self, message: Message):
        """Send music for programming"""
        await message.edit(self.strings["fetching"])

        rss_url = "https://musicforprogramming.net/rss.xml"
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            await message.edit("Failed to fetch music.")
            return

        random_entry = random.choice(feed.entries)

        title = random_entry.title
        description = random_entry.description
        link = random_entry.link
        download_url = random_entry.enclosures[0].href

        if not download_url:
            await utils.answer(message, "Failed to fetch music.")
            return

        await self.inline.form(
            text=f"<b>{title}</b>\n\n<b>Description:</b> {description}",
            message=message,
            reply_markup=[
                [{"text": "Link 🔗", "url": link}],
                [
                    {
                        "text": "Download ⬇️",
                        "callback": lambda c, u=download_url, l=link, t=title: self.download_and_send_music(
                            c, message.chat_id, u, t, l
                        ),
                    }
                ],
                [{"text": "Close ❌", "callback": self.close}],
            ],
            silent=True,
        )

    async def close(self, call):
        """Close the inline form"""
        await call.delete()

    async def download_and_send_music(
        self,
        call: InlineCall,
        chat_id: int,
        download_url: str,
        title: str,
        link: str,
    ):
        await call.edit(
            text=f"<b>Title: {title}</b>\n<b>Link: {link}</b>\n\n"
            + self.strings("downloading")
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    return

                file = await response.read()

        extension = download_url.split(".")[-1]

        temp_file_path = os.path.join(os.getcwd(), f"chill.{extension}")
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file)

        await self.client.send_file(
            chat_id,
            temp_file_path,
            voice=True,
            only_document=False,
            caption=self.strings("successful")
            + f"\n\n<b>Title: {utils.escape_html(title)}</b>\n<b>Link:"
            f" {utils.escape_html(link)}</b>",
        )

        os.remove(temp_file_path)
        await call.delete()
