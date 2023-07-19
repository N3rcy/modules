
#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴ 
 
# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

import requests
from bs4 import BeautifulSoup
from hikkatl.types import Message
from .. import loader, utils
from deep_translator import GoogleTranslator


@loader.tds
class EmojiInfo(loader.Module):
    """Module for retrieving information about emojis from emojipedia.org"""
    strings = {"name": "EmojiInfo", 
    "emoji_not_found": "Emoji not found.", 
    "error": "Error occurred while retrieving emoji information. Error: "
    }

    strings_ru = {"emoji_not_found": "Эмодзи не найдено.",
    "error": "Произошла ошибка при получении информации об эмодзи. Ошибка: "
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(ru_doc="Получить информацию об эмодзи")
    async def emoji(self, m: Message):
        """Retrieve information about an emoji"""
        emoji = utils.get_args_raw(m)
        if not emoji:
            await utils.answer(m, self.strings["emoji_not_found"])
            return

        try:
            url = f"https://emojipedia.org/{emoji}/"
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            emoji_name = soup.find("h1").get_text(strip=True)
            emoji_description = soup.find(class_="description").get_text(strip=True)
            emoji_codepoints = soup.find("h2", text="Codepoints").find_next("ul").find("li").get_text(strip=True)
            
            # Remove unnecessary parts from description
            if "Emoji Meaning" in emoji_description:
                emoji_description = emoji_description.split("Emoji Meaning", 1)[1]
            emoji_description = emoji_description.split("Copy and Paste")[0].strip()
            
            info_text = f"<b>Name: {emoji_name}</b>\n<b>Description:</b> {emoji_description}\n<b>Codepoints:</b> {emoji_codepoints}"
            lang = self.db.get("hikka.translations", "lang")
            if lang == "en":
                await utils.answer(m, info_text)
            else: 
                translator = GoogleTranslator(source='auto', target=lang)
                translation = translator.translate(info_text)
                await utils.answer(m, translation)
        except Exception as e:
            await utils.answer(m, self.strings["error"] + str(e))
