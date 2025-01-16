#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2
# requires: bs4

import requests
from bs4 import BeautifulSoup
from hikkatl.tl.types import Message

from .. import loader, utils


@loader.tds
class EmojiInfo(loader.Module):
    """Module for retrieving information about emojis from emojipedia.org"""

    strings = {
        "name": "EmojiInfo",
        "emoji_not_found": "Emoji not found.",
        "error": "Error occurred while retrieving emoji information. Error: ",
    }

    strings_ru = {
        "emoji_not_found": "Эмодзи не найдено.",
        "error": "Произошла ошибка при получении информации об эмодзи. Ошибка: ",
    }

    @loader.command(ru_doc="Получить информацию об эмодзи")
    async def emoji(self, message: Message):
        """Retrieve information about an emoji"""
        if not (emoji := utils.get_args_raw(message)):
            await utils.answer(message, self.strings["emoji_not_found"])
            return

        try:
            url = f"https://emojipedia.org/{emoji}/"
            response = await utils.run_sync(requests.get, url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            emoji_name = soup.find('title').text
            emoji_description = soup.find('div', {'class': 'HtmlContent_html-content-container__Ow2Bk'}).text
            emoji_codepoints = ' '.join(['U+{:X}'.format(ord(char)) for char in emoji])

            await utils.answer(
                message,
                (
                    f"<b>Name: {utils.escape_html(emoji_name)}</b>\n<b>Description:</b>"
                    f" {utils.escape_html(emoji_description)}\n<b>Codepoints:</b>"
                    f" {utils.escape_html(emoji_codepoints)}"
                ),
            )

        except Exception as e:
            await utils.answer(
                message, self.strings("error") + utils.escape_html(str(e))
            )
