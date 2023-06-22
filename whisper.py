
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
import openai
from pydub import AudioSegment
import json

from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class WhisperMod(loader.Module):
    """Module for speech recognition"""
    strings = {
        "name": "WhisperMod",
        "audio_not_found": "<b><emoji document_id=5818678700274617758>👮‍♀️</emoji>Not found to recognize.</b>",
        "recognized": "<b><emoji document_id=5821302890932736039>🗣</emoji>Recognized:</b>\n{transcription}",
        "error": "<b><emoji document_id=5980953710157632545>❌</emoji>Error occurred during transcription.</b>",
        "recognition": "<b><emoji document_id=5307937750828194743>🫥</emoji>Recognition...</b>",
        "downloading": "Downloading, wait"
    }

    strings_ru = {
        "audio_not_found": "<b><emoji document_id=5818678700274617758>👮‍♀️</emoji>Не найдено, что распознавать.</b>",
        "recognized": "<b><emoji document_id=5821302890932736039>🗣</emoji>Распознано:</b>\n{transcription}",
        "error": "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка при транскрипции.</b>",
        "recognition": "<b><emoji document_id=5307937750828194743>🫥</emoji>Распознавание...</b>",
        "downloading": "<b><emoji document_id=5310189005181036109>🐍</emoji>Скачивание, подождите...</b>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "Api key for Whisper",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "temperature",
                '0.2',
                lambda: "The sampling temperature, between 0 and 1. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. If set to 0, the model will use log probability to automatically increase the temperature until certain thresholds are hit.",
                validator=loader.validators.String(),         
            ),
            loader.ConfigValue(
                "prompt",
                None,
                lambda: "An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language.",
                validator=loader.validators.String(),
            )
        )
    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(ru_doc="распознать речь из голосового/видео сообщения в реплае")
    async def whisper(self, m: Message):
        """Transcribe speech from a voice/video message in reply"""
        reply = await m.get_reply_message()
        if not reply or not reply.file:
            await utils.answer(m, self.strings["audio_not_found"])
            return

        await utils.answer(m, self.strings["downloading"])
        file = await reply.download_media()
        file_extension = os.path.splitext(file)[1].lower()

        openai.api_key = self.config["api_key"]

        if file_extension == ".oga":
            await utils.answer(m, self.strings["recognition"])
            input_file = file

            audio = AudioSegment.from_file(input_file, format="ogg")
            audio.export("output_file.mp3", format="mp3")

            audio_file = open("output_file.mp3", "rb")
            response = openai.Audio.transcribe("whisper-1", audio_file, prompt=self.config["prompt"], temperature = self.config["temperature"])
            response_dict = response.to_dict()
            transcription = response_dict['text']
            await utils.answer(m, self.strings["recognized"].format(transcription=transcription))
            os.remove(file)
            os.remove("output_file.mp3")

        elif file_extension == ".mp4":
            await utils.answer(m, self.strings["recognition"])
            input_file = file

            audio_file = open(input_file, "rb")
            response = openai.Audio.transcribe("whisper-1", audio_file, prompt=self.config["prompt"], temperature = self.config["temperature"])
            response_dict = response.to_dict()
            transcription = response_dict['text']
            await utils.answer(m, self.strings["recognized"].format(transcription=transcription))
            os.remove(file)

        elif file_extension == ".mp3":
            await utils.answer(m, self.strings["recognition"])
            input_file = file

            audio_file = open(input_file, "rb")
            response = openai.Audio.transcribe("whisper-1", audio_file, prompt=self.config["prompt"], temperature = self.config["temperature"])
            response_dict = response.to_dict()
            transcription = response_dict['text']
            await utils.answer(m, self.strings["recognized"].format(transcription=transcription))
            os.remove(file)

        elif file_extension == ".m4a":
            await utils.answer(m, self.strings["recognition"])
            input_file = file

            audio_file = open(input_file, "rb")
            response = openai.Audio.transcribe("whisper-1", audio_file, prompt=self.config["prompt"], temperature = self.config["temperature"])
            response_dict = response.to_dict()
            transcription = response_dict['text']
            await utils.answer(m, self.strings["recognized"].format(transcription=transcription))
            os.remove(file)

        else:
            await utils.answer(m, self.strings["audio_not_found"])
