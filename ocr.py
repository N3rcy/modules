
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
import requests
import json
from hikkatl.types import Message
from telethon.tl.types import MessageMediaPhoto
from .. import loader, utils

@loader.tds
class OCRMod(loader.Module):
    """Module for Optical Character Recognition"""
    strings = {
        "name": "OCRMod",
        "file_not_found": "<b><emoji document_id=5980953710157632545>❌</emoji>Not found to recognize, please reply.</b>",
        "error": f"<b><emoji document_id=5980953710157632545>❌</emoji>An error occurred while processing the image. Error: </b>",
        "text_result": "<b><emoji document_id=6041850934756119589>🫠</emoji>Recognized:</b>\n",
        "recognition": "<b><emoji document_id=5307937750828194743>🫥</emoji>Recognition...</b>"
    }

    strings_ru = {
        "file_not_found": "<b><emoji document_id=5980953710157632545>❌</emoji>Не найдено, что распознавать, ответь реплаем.</b>",
        "error": f"<b><emoji document_id=5980953710157632545>❌</emoji>Произошла ошибка при обработке изображения. Ошибка: </b>",
        "text_result": "<b><emoji document_id=6041850934756119589>🫠</emoji>Распознано:</b>\n",
        "recognition": "<b><emoji document_id=5307937750828194743>🫥</emoji>Распознаю...</b>"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                "K81805939388957",
                lambda: "api key for OCR", 
                validator=loader.validators.Hidden(), 
            ),
            loader.ConfigValue(
                "language",
                "eng",
                lambda: "language on the photo",
            ),
        )

    def ocr_space_file(self, filename, overlay=False):
        """OCR.space API request with local file."""
        api_key=self.config['api_key']
        language=self.config['language']

        payload = {'isOverlayRequired': overlay,
                   'apikey': api_key,
                   'language': language,
                   }
        with open(filename, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image',
                              files={filename: f},
                              data=payload,
                              )
        return r.content.decode()

    @loader.command(ru_doc="Распознать текст на фото из реплая", en_doc="Recognize text from an image in reply")
    async def ocr(self, m: Message):
        """Recognize text from an image in reply"""
        reply_msg = await m.get_reply_message()
        if not reply_msg or not isinstance(reply_msg.media, MessageMediaPhoto):
            await utils.answer(m, self.strings["file_not_found"])
            return
        try:
            await utils.answer(m, self.strings['recognition'])
            filename = await reply_msg.download_media(file='image.png')
            result = self.ocr_space_file(filename)
            os.remove(filename)

            parsed_result = json.loads(result)
            parsed_text = parsed_result["ParsedResults"][0]["ParsedText"]

            await utils.answer(m, f"{self.strings['text_result']}\n{parsed_text}")
        except Exeption as e:
            await utils.answer(m, self.strings['error'] + str(e))
        