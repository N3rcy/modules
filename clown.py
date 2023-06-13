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
import tempfile
from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class ClownModule(loader.Module):
    """Модуль для клоунизации 'pov - <username>'"""
    strings = {
        "name": "ClownMod",
        "video_not_found": "<b><emoji document_id=5980953710157632545>❌</emoji>Error inside module. (video_not_found)</b>",
        "processing": "<b><emoji document_id=5334643333488713810>🌐</emoji>Processing video...</b>",
        "sending": "<b><emoji document_id=5371074117971745503>🤡</emoji>Sending video...</b>",
        "error_downloading": "<b><emoji document_id=5980953710157632545>❌</emoji>Error inside module. (error_downloading)</b>",
        "error_sending": "<b><emoji document_id=5980953710157632545>❌</emoji>There was an error uploading the video</b>",
    }
    strings_ru = {
        "video_not_found": "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка внутри модуля.</b>",
        "processing": "<b><emoji document_id=5334643333488713810>🌐</emoji>Обработка видео...</b>",
        "sending": "<b><emoji document_id=5371074117971745503>🤡</emoji>Отправка видео...</b>",
        "error_downloading": "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка при загрузке видео.</b>",
        "error_sending": "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка при отправке видео.</b>",
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(ru_doc="Сделать клавном <ник> или реплай")
    async def clown(self, m: Message):
        """Добавляет текст поверх видео"""
        reply_message = await m.get_reply_message()
        if reply_message and reply_message.sender_id:
            username = "pov - " + await self.get_username(reply_message.sender_id)
        else:
            username = "pov - " + utils.get_args_raw(m)

        if not username:
            await utils.answer(m, self.strings_ru["video_not_found"])
            return

        video_url = "https://0x0.st/HcEt.mp4"

        with tempfile.TemporaryDirectory() as temp_dir:
            video_path = os.path.join(temp_dir, "clown_video.mp4")
            output_path = os.path.join(temp_dir, "clown_output.mp4")

            await utils.answer(m, self.strings_ru["processing"])

            # Download the video
            try:
                response = requests.get(video_url)
                with open(video_path, "wb") as f:
                    f.write(response.content)
            except Exception:
                await utils.answer(m, self.strings_ru["error_downloading"])
                return

            # Add text overlay on the video
            command = f"ffmpeg -i {video_path} -vf \"drawtext=text='{username}':fontsize=50:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/4-150\" -c:a copy {output_path}"
            os.system(command)

            await utils.answer(m, self.strings_ru["sending"])

            # Send the modified video
            try:
                await self.client.send_file(m.chat_id, output_path, video_note=True)
            except Exception:
                await utils.answer(m, self.strings_ru["error_sending"])

            await m.delete()

        # Delete the temporary files (automatically handled by TemporaryDirectory)

    async def get_username(self, user_id):
        user = await self.client.get_entity(user_id)
        return user.username if user.username else user.first_name
