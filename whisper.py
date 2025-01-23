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

import requests
import base64

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
        "hf_instructions": (
        "<emoji document_id=5238154170174820439>👩‍🎓</emoji> <b>How to get hugging face api token:</b>\n"
        "<b>&gt; Open Hugging Face and sign in.</b> <emoji document_id=4904848288345228262>👤</emoji> <b>\n"
        "&gt; Go to Settings → Access Tokens: </b><a href=\"https://huggingface.co/settings/tokens\"><b>https://huggingface.co/settings/tokens</b></a><b>.</b> <emoji document_id=5222142557865128918>⚙️</emoji> <b>\n"
        "&gt; Click New Token.</b> <emoji document_id=5431757929940273672>➕</emoji> <b>\n"
        "&gt; Select permission: \"make calls to the serverless Inference API\".</b> <emoji document_id=5253952855185829086>⚙️</emoji> <b>\n"
        "&gt; Click Create Token.</b> <emoji document_id=5253652327734192243>➕</emoji> <b>\n"
        "&gt; Copy the token and paste it into the config.</b> <emoji document_id=4916036072560919511>✅</emoji>"
        ),
        "hf_token_missing": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Missing hugging face api token</b>"
            " (<code>.cfg whispermod</code>)"
        )
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
        "no_api": (
            "<b><emoji document_id=5980953710157632545>❌</emoji> Укажите api-ключ в конфиге</b>"
            " (<code>.cfg whispermod</code>)"
        ),
        "invalid_key": (
            "<b><emoji document_id=5980953710157632545>❌</emoji> Неверный api-ключ</b>"
        ),
        "hf_instructions": (
            "<emoji document_id=5238154170174820439>👩‍🎓</emoji> <b>Как получить api-токен hugging face:</b>\n"
            "<b>&gt; Откройте Hugging Face и войдите в аккаунт. </b><emoji document_id=4904848288345228262>👤</emoji><b>\n"
            "&gt; Перейдите в Settings → Access Tokens: </b><a href=\"https://huggingface.co/settings/tokens\"><b>https://huggingface.co/settings/tokens</b></a><b>. </b><emoji document_id=5222142557865128918>⚙️</emoji><b>\n"
            "&gt; Нажмите New Token. </b><emoji document_id=5431757929940273672>➕</emoji><b>\n"
            "&gt; Выберите разрешение: \"make calls to the serverless Inference API\". </b><emoji document_id=5253952855185829086>⚙️</emoji><b>\n"
            "&gt; Нажмите Create Token. </b><emoji document_id=5253652327734192243>➕</emoji><b>\n"
            "&gt; Скопируйте токен и вставьте его в конфиг. </b><emoji document_id=4916036072560919511>✅</emoji>"
        ),
        "hf_token_missing": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Отсутствует api-токен hugging face</b>"
            " (<code>.cfg whispermod</code>)"
        )
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
            loader.ConfigValue(
                "hf_api_key",
                None,
                lambda: "Api key for hugging face (look .hfguide)",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
            "auto_voice",
                True,
                lambda: "Enable auto-recognition for voice messages",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "auto_video",
                True,
                lambda: "Enable auto-recognition for video messages",
                validator=loader.validators.Boolean()
            ),
        )

    @loader.command(ru_doc="распознать речь из голосового/видео сообщения в реплае, используя openai api")
    async def whisper(self, message: Message):
        """Transcribe speech from a voice/video message in reply using openai api"""
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
            if (message.voice and self.config["auto_voice"]) or (message.video and self.config["auto_video"]):
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
        else:
            return

    @loader.command(ru_doc="распознать речь из голосового/видео сообщения в реплае, используя hugging face api")
    async def hfwhisper(self, m: Message):
        """Transcribe speech from a voice/video message in reply using hugging face api"""
        
        if self.config["hf_api_key"] is None:
            await utils.answer(m, self.strings["hf_token_missing"])
            return
        
        rep = await m.get_reply_message()
        await utils.answer(m, self.strings["downloading"])
        file = await rep.download_media()
        file_extension = os.path.splitext(file)[1].lower()
        if file_extension in ['.ogg', '.oga']:
            try:
                await utils.answer(m, self.strings["recognition"])
                with open(file, "rb") as f:
                    audio_bytes = f.read()
                
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                payload = {
                    "inputs": audio_b64,
                }
                
                response = await utils.run_sync(
                    requests.post,
                    url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
                    headers = {"Authorization": f"Bearer {self.config['hf_api_key']}",
                    "x-use-cache": "false",       
                    "x-wait-for-model": "true",   
                    "Content-Type": "application/json"  
                    },
                    json = payload,
                )
                output = response.json()
                os.remove(file)
                return await utils.answer(m, self.strings["recognized"].format(transcription=output['text']))
            
            except Exception as e:
                import logging
                logging.getLogger().error(e)
                return await utils.answer(m, self.strings["error"])
        elif file_extension in [".mp3", "m4a", ".wav", ".mpeg", ".mp4"]:
            try:
                await utils.answer(m, self.strings["recognition"])
                audio = AudioSegment.from_file(file, format=file_extension.replace('.', ''))
                audio.export("output_file.mp3", format="mp3")
                with open("output_file.mp3", "rb") as f:
                    audio_bytes = f.read()
                
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                
                payload = {
                    "inputs": audio_b64,
                    "language": "ru",
                    "attention_mask": [1] * len(audio_bytes)  
                }
                
                response = await utils.run_sync(
                    requests.post,
                    url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
                    headers = {"Authorization": f"Bearer {self.config['hf_api_key']}",
                    "x-use-cache": "false",       
                    "x-wait-for-model": "true",   
                    "Content-Type": "application/json"  
                    },
                    json = payload,
                )
                output = response.json()
                os.remove("output_file.mp3")
                os.remove(file)
                return await utils.answer(m, self.strings["recognized"].format(transcription=output['text']))
            
            except Exception as e:
                import logging
                logging.getLogger().error(e)
                return await utils.answer(m, self.strings["error"])
            
    @loader.command(
        ru_doc=(
            "включить/выключить автораспознавание через Hugging Face API в текущем чате"
        )
    )
    async def hfautowhspr(self, message: Message):
        """Enable/disable auto-speech recognition using Hugging Face API"""
        chat_id = str(message.chat_id)
        current_state = self.get("hfautowhspr", {})
        enabled = current_state.get(chat_id, False)

        if enabled:
            current_state.pop(chat_id, None)
            status_message = self.strings["autowhisper_disabled"]
        else:
            current_state[chat_id] = True
            status_message = self.strings["autowhisper_enabled"]
        self.set("hfautowhspr", current_state)
        await utils.answer(message, status_message)

    @loader.watcher(only_media=True)
    async def hfautowhisper_watcher(self, message: Message):
        """Watcher for Hugging Face auto-transcription"""
        chat_id = str(message.chat_id)
        current_state = self.get("hfautowhspr", {})

        if current_state.get(chat_id, False):
            if (message.voice and self.config["auto_voice"]) or (message.video and self.config["auto_video"]):
                if not message.gif and not message.sticker and not message.photo:
                    rep = message
                    await self.hfwhisperwatch(rep)

    async def hfwhisperwatch(self, message: Message):
        """Auto-transcribe using Hugging Face API"""
        if self.config["hf_api_key"] is None:
            return

        rep = message
        down = await self.client.send_message(
            message.chat.id, self.strings["downloading"], reply_to=rep.id
        )
        file = await rep.download_media()
        file_extension = os.path.splitext(file)[1].lower()

        try:
            await self.client.edit_message(
                message.chat_id, down.id, self.strings["recognition"]
            )

            if file_extension in ['.ogg', '.oga']:
                with open(file, "rb") as f:
                    audio_bytes = f.read()
            else:
                audio = AudioSegment.from_file(file, format=file_extension.replace('.', ''))
                audio.export("temp_audio.mp3", format="mp3")
                with open("temp_audio.mp3", "rb") as f:
                    audio_bytes = f.read()
                os.remove("temp_audio.mp3")

            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            response = await utils.run_sync(
                requests.post,
                url="https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
                headers={
                    "Authorization": f"Bearer {self.config['hf_api_key']}",
                    "x-use-cache": "false",
                    "x-wait-for-model": "true",
                    "Content-Type": "application/json"
                },
                json={"inputs": audio_b64},
            )

            if response.status_code != 200:
                raise Exception(f"API Error: {response.text}")

            output = response.json()
            text = output.get('text', '')
            
            await self.client.edit_message(
                message.chat_id,
                down.id,
                self.strings["recognized"].format(transcription=text),
            )

        except Exception as e:
            await self.client.edit_message(
                message.chat_id,
                down.id,
                f"<b>❌ Error: {str(e)}</b>"
            )
        finally:
            if os.path.exists(file):
                os.remove(file)
            if os.path.exists("temp_audio.mp3"):
                os.remove("temp_audio.mp3")
    
    @loader.command(ru_doc="гайд как получить hugging face токен", en_doc="guide how to get hugging face token")
    async def hfguide(self, m: Message):
        await utils.answer(m, self.strings['hf_instructions'])