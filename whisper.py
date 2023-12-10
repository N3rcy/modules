#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2
# requires: pydub openai==1.3.8 ffmpeg

import os

import openai
from hikkatl.tl.types import Message
from pydub import AudioSegment

from .. import loader, utils


@loader.tds
class WhisperMod(loader.Module):
    """Module for speech recognition"""

    strings = {
        "name": "WhisperMod",
        "audio_not_found": (
            "<b><emoji document_id=5818678700274617758>👮‍♀️</emoji>Not found to"
            " recognize.</b>"
        ),
        "recognized": (
            "<b><emoji"
            " document_id=5821302890932736039>🗣</emoji>Recognized:</b>\n{transcription}"
        ),
        "error": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Error occurred during"
            " transcription.</b>"
        ),
        "recognition": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Recognition...</b>"
        ),
        "downloading": "<b><emoji document_id=5310189005181036109>🐍</emoji>Downloading, wait</b>",
        "autowhisper_enabled": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Auto-whisper enabled"
            " in this chat.</b>"
        ),
        "autowhisper_disabled": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Auto-whisper disabled"
            " in this chat.</b>"
        ),
        "no_api": "<b><emoji document_id=5980953710157632545>❌</emoji> Insert openai api-key in config</b> (<code>.cfg whispermod</code>)",
        "invalid_key": "<b><emoji document_id=5980953710157632545>❌</emoji> Invalid openai api-key</b>",
    }

    strings_ru = {
        "audio_not_found": (
            "<b><emoji document_id=5818678700274617758>👮‍♀️</emoji>Не найдено, что"
            " распознавать.</b>"
        ),
        "recognized": (
            "<b><emoji"
            " document_id=5821302890932736039>🗣</emoji>Распознано:</b>\n{transcription}"
        ),
        "error": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка при"
            " транскрипции.</b>"
        ),
        "recognition": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Распознавание...</b>"
        ),
        "downloading": (
            "<b><emoji document_id=5310189005181036109>🐍</emoji>Скачивание,"
            " подождите...</b>"
        ),
        "autowhisper_enabled": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Автораспознавание"
            " включено в этом чате.</b>"
        ),
        "autowhisper_disabled": (
            "<b><emoji document_id=5307937750828194743>🫥</emoji>Автораспознавание"
            " отключено в этом чате.</b>"
        ),
        "no_api": "<b><emoji document_id=5980953710157632545>❌</emoji> Укажите api-ключ в конфиге</b> (<code>.cfg whispermod</code>)",
        "invalid_key": "<b><emoji document_id=5980953710157632545>❌</emoji> Неверный api-ключ</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "Api key for Whisper (https://platform.openai.com/account/api-keys)",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "temperature",
                "0.2",
                lambda: (
                    "The sampling temperature, between 0 and 1. Higher values like 0.8"
                    " will make the output more random, while lower values like 0.2"
                    " will make it more focused and deterministic. If set to 0, the"
                    " model will use log probability to automatically increase the"
                    " temperature until certain thresholds are hit."
                ),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "prompt",
                None,
                lambda: (
                    "An optional text to guide the model's style or continue a previous"
                    " audio segment. The prompt should match the audio language."
                ),
                validator=loader.validators.String(),
            ),
        )

    @loader.command(ru_doc="распознать речь из голосового/видео сообщения в реплае")
    async def whisper(self, message: Message):
        """Transcribe speech from a voice/video message in reply"""
        if self.config["api_key"] is None:
            await utils.answer(message, self.strings["no_api"])
            return
        rep = await message.get_reply_message()
        down = await utils.answer(message, self.strings["downloading"])
        file = await rep.download_media()
        file_extension = os.path.splitext(file)[1].lower()

        if file_extension in [".oga", ".ogg"]:
            await self.client.edit_message(
                message.chat_id, down.id, self.strings["recognition"]
            )
            input_file = file

            audio = AudioSegment.from_file(input_file, format="ogg")
            audio.export("output_file.mp3", format="mp3")

            audio_file = open("output_file.mp3", "rb")

            client = openai.AsyncOpenAI(api_key=self.config["api_key"])
            try:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=self.config["prompt"],
                    temperature=self.config["temperature"],
                )
            except openai.AuthenticationError:
                await utils.answer(message, self.strings["invalid_key"])
                return
            except Exception as e:
                await utils.answer(
                    message,
                    f"<b><emoji document_id=5980953710157632545>❌</emoji>Error: {e}</b>",
                )
                return
            transcription = response.text
            await self.client.edit_message(
                message.chat_id,
                down.id,
                self.strings["recognized"].format(transcription=transcription),
            )
            os.remove(file)
            os.remove("output_file.mp3")
        elif file_extension in [".mp3", "m4a", ".wav", ".mpeg", ".mp4"]:
            await self.client.edit_message(
                message.chat_id, down.id, self.strings["recognition"]
            )
            input_file = file

            audio_file = open(input_file, "rb")

            client = openai.AsyncOpenAI(api_key=self.config["api_key"])
            try:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=self.config["prompt"],
                    temperature=self.config["temperature"],
                )
            except openai.AuthenticationError:
                await utils.answer(message, self.strings["invalid_key"])
                return
            except Exception as e:
                await utils.answer(
                    message,
                    f"<b><emoji document_id=5980953710157632545>❌</emoji>Error: {e}</b>",
                )
                return
            transcription = response.text
            await self.client.edit_message(
                message.chat_id,
                down.id,
                self.strings["recognized"].format(transcription=transcription),
            )
            os.remove(file)
            os.remove("output_file.mp3")
        else:
            await utils.answer(message, self.strings["audio_not_found"])

    @loader.command(
        ru_doc=(
            "включить/выключить автораспознавание голосовых и видео сообщений в чате"
            " где введена команда"
        )
    )
    async def autowhspr(self, message: Message):
        """Enable/disable auto-speech recognition for voice and video messages"""
        chat_id = str(message.chat_id)
        current_state = self.get("autowhspr", {})
        enabled = current_state.get(chat_id, False)

        if enabled:
            current_state.pop(chat_id, None)
            status_message = self.strings["autowhisper_disabled"]
        else:
            current_state[chat_id] = True
            status_message = self.strings["autowhisper_enabled"]
        self.set("autowhspr", current_state)
        await utils.answer(message, status_message)

    @loader.watcher(only_media=True)
    async def autowhisper_watcher(self, message: Message):
        """Watcher to automatically transcribe voice and video messages when auto-speech recognition is enabled"""
        chat_id = str(message.chat_id)
        current_state = self.get("autowhspr", {})

        if current_state.get(chat_id, False):
            if message.voice or message.video:
                if not message.gif and not message.sticker and not message.photo:
                    rep = message
                    await self.whisperwatch(rep)

    async def whisperwatch(self, message: Message):
        """Transcribe speech from a voice/video message in reply"""
        rep = message
        down = await self.client.send_message(
            message.chat.id, message=self.strings["downloading"], reply_to=rep.id
        )
        file = await rep.download_media()
        file_extension = os.path.splitext(file)[1].lower()

        if file_extension in [".oga", ".ogg"]:
            await self.client.edit_message(
                message.chat_id, down.id, self.strings["recognition"]
            )
            input_file = file

            audio = AudioSegment.from_file(input_file, format="ogg")
            audio.export("output_file.mp3", format="mp3")

            audio_file = open("output_file.mp3", "rb")

            client = openai.AsyncOpenAI(api_key=self.config["api_key"])
            try:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=self.config["prompt"],
                    temperature=self.config["temperature"],
                )
            except openai.AuthenticationError:
                await utils.answer(message, self.strings["invalid_key"])
                return
            except Exception as e:
                await utils.answer(
                    message,
                    f"<b><emoji document_id=5980953710157632545>❌</emoji>Error: {e}</b>",
                )
                return
            transcription = response.text
            await self.client.edit_message(
                message.chat_id,
                down.id,
                self.strings["recognized"].format(transcription=transcription),
            )
            os.remove(file)
            os.remove("output_file.mp3")
        elif file_extension in [".mp3", "m4a", ".wav", ".mpeg", ".mp4"]:
            await self.client.edit_message(
                message.chat_id, down.id, self.strings["recognition"]
            )
            input_file = file

            audio_file = open(input_file, "rb")

            client = openai.AsyncOpenAI(api_key=self.config["api_key"])
            try:
                response = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt=self.config["prompt"],
                    temperature=self.config["temperature"],
                )
            except openai.AuthenticationError:
                await utils.answer(message, self.strings["invalid_key"])
                return
            except Exception as e:
                await utils.answer(
                    message,
                    f"<b><emoji document_id=5980953710157632545>❌</emoji>Error: {e}</b>",
                )
                return
            transcription = response.text
            await self.client.edit_message(
                message.chat_id,
                down.id,
                self.strings["recognized"].format(transcription=transcription),
            )
            os.remove(file)
            os.remove("output_file.mp3")
        else:
            return
