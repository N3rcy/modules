#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2
# scope: ffmpeg

import os
import shlex
import subprocess
import tempfile

import requests
from hikkatl.tl.types import Message

from .. import loader, utils


@loader.tds
class ClownModule(loader.Module):
    """Модуль для клоунизации 'pov - <username>'"""

    strings = {
        "name": "ClownMod",
        "video_not_found": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Error inside module."
            " (video_not_found)</b>"
        ),
        "processing": (
            "<b><emoji document_id=5334643333488713810>🌐</emoji>Processing"
            " video...</b>"
        ),
        "sending": (
            "<b><emoji document_id=5371074117971745503>🤡</emoji>Sending video...</b>"
        ),
        "error_downloading": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Error inside module."
            " (error_downloading)</b>"
        ),
        "error_sending": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>There was an error"
            " uploading the video</b>"
        ),
    }
    strings_ru = {
        "video_not_found": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка внутри"
            " модуля.</b>"
        ),
        "processing": (
            "<b><emoji document_id=5334643333488713810>🌐</emoji>Обработка видео...</b>"
        ),
        "sending": (
            "<b><emoji document_id=5371074117971745503>🤡</emoji>Отправка видео...</b>"
        ),
        "error_downloading": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка при загрузке"
            " видео.</b>"
        ),
        "error_sending": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка при отправке"
            " видео.</b>"
        ),
    }

    @loader.command(ru_doc="Сделать клавном <ник> или реплай")
    async def clown(self, message: Message):
        """Добавляет текст поверх видео"""
        if not (
            username := "pov - "
            + (
                await self._get_username(reply_message.sender_id)
                if (reply_message := await message.get_reply_message())
                else utils.get_args_raw(message)
            )
        ):
            await utils.answer(message, self.strings("video_not_found"))
            return

        video_url = "https://github.com/N3rcy/modules/raw/refs/heads/main/clown_asset.mp4"

        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, "clown_video.mp4")
            output_path = os.path.join(temp_dir, "clown_output.mp4")

            await utils.answer(message, self.strings("processing"))

            try:
                response = await utils.run_sync(requests.get, video_url)
                response.raise_for_status()
                with open(video_path, "wb") as f:
                    f.write(response.content)
            except Exception:
                await utils.answer(message, self.strings("error_downloading"))
                return

            command = f"ffmpeg -i {video_path} -vf \"drawtext=text='{username}':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/4-150\" -c:a copy {output_path}"
            os.system(command)
            await utils.answer(message, self.strings("sending"))

            try:
                await utils.answer_file(
                    message,
                    output_path,
                    video_note=True,
                )
            except Exception:
                await utils.answer(message, self.strings("error_sending"))

    async def _get_username(self, user_id: int) -> str:
        user = await self.client.get_entity(user_id, exp=0)
        return user.username or user.first_name
