#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

import json
import os

import requests
from hikkatl.tl.types import Message, MessageMediaPhoto

from .. import loader, utils


@loader.tds
class OCRMod(loader.Module):
    """Module for Optical Character Recognition"""

    strings = {
        "name": "OCRMod",
        "file_not_found": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Not found to"
            " recognize, please reply.</b>"
        ),
        "error": (
            f"<b><emoji document_id=5980953710157632545>❌</emoji>An error occurred"
            f" while processing the image. Error: </b>"
        ),
        "text_result": (
            "<b><emoji document_id=6041850934756119589>🫠</emoji>Recognized:</b>\n"
        ),
        "recognition": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Recognition...</b>"
        ),
        "no_api": "<b><emoji document_id=5980953710157632545>❌</emoji> Please insert api-key in config</b> (<code>.cfg ocrmod</code>)",
        "config_key": "Get key here: https://ocr.space/ocrapi/freekey",
        "language": ("🌐 Recognition language, available can be viewed here:"
                     "https://ocr.space/OCRAPI#:~:text=faster%20upload%20speeds.-,language,-%5BOptional%5D%0AArabic"),
    }

    strings_ru = {
        "file_not_found": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Не найдено, что"
            " распознавать, ответь реплаем.</b>"
        ),
        "error": (
            f"<b><emoji document_id=5980953710157632545>❌</emoji>Произошла ошибка при"
            f" обработке изображения. Ошибка: </b>"
        ),
        "text_result": (
            "<b><emoji document_id=6041850934756119589>🫠</emoji>Распознано:</b>\n"
        ),
        "recognition": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Распознаю...</b>"
        ),
        "no_api": "<b><emoji document_id=5980953710157632545>❌</emoji> Пожалуйста, вставьте api-key в конфиг</b> (<code>.cfg ocrmod</code>)",
        "config_key": "Получить ключ можно здесь: https://ocr.space/ocrapi/freekey",
        "language": ("🌐 Язык распознавания, доступные можно посмотреть здесь:"
                     "https://ocr.space/OCRAPI#:~:text=faster%20upload%20speeds.-,language,-%5BOptional%5D%0AArabic"),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: self.strings['config_key'],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "language",
                "eng",
                lambda: self.strings['language'],
            ),
        )

    async def ocr_space_file(self, filename, overlay=False):
        """OCR.space API request with local file."""
        api_key = self.config["api_key"]
        language = self.config["language"]

        payload = {
            "isOverlayRequired": overlay,
            "apikey": api_key,
            "language": language,
        }
        with open(filename, "rb") as f:
            r = await utils.run_sync(
                requests.post,
                "https://api.ocr.space/parse/image",
                files={filename: f},
                data=payload,
            )
        return r.content.decode()

    @loader.command(
        ru_doc="Распознать текст на фото из реплая",
        en_doc="Recognize text from an image in reply",
    )
    async def ocr(self, message: Message):
        """Recognize text from an image in reply"""
        if not (reply_msg := await message.get_reply_message()) or not isinstance(
            reply_msg.media, MessageMediaPhoto
        ):
            await utils.answer(message, self.strings("file_not_found"))
            return

        if self.config['api_key'] == None:
            await utils.answer(message, self.strings['no_api'])
            return

        try:
            await utils.answer(message, self.strings("recognition"))
            filename = await reply_msg.download_media(file="image.png")
            result = await self.ocr_space_file(filename)
            os.remove(filename)

            parsed_result = json.loads(result)
            parsed_text = parsed_result["ParsedResults"][0]["ParsedText"]

            await utils.answer(
                message,
                f"{self.strings('text_result')}\n{utils.escape_html(parsed_text)}",
            )
        except Exception as e:
            await utils.answer(
                message, self.strings("error") + utils.escape_html(str(e))
            )
