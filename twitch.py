#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2
# reqires: youtube_dl

import youtube_dl
from hikkatl.tl.types import Message

from .. import loader, utils


@loader.tds
class TwitchModule(loader.Module):
    """Module for downloading Twitch clips and videos"""

    strings = {
        "name": "Twitchdl",
        "clip_download_started": (
            "<emoji document_id=5307773751796964107>⏳</emoji><b>Clip download started,"
            " please wait.</b>"
        ),
        "clip_download_completed": (
            "<b><emoji document_id=5215480011322042129>➡️</emoji>Clip download"
            " completed. Sending...</b>"
        ),
        "clip_download_failed": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Clip download failed."
            " Ensure the correctness of the link.</b>"
        ),
        "video_download_started": (
            "<b><emoji document_id=5307773751796964107>⏳</emoji>Video download"
            " started, please wait.</b>"
        ),
        "video_download_completed": (
            "<b><emoji document_id=5215480011322042129>➡️</emoji>Video download"
            " completed. Sending...</b>"
        ),
        "video_download_failed": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Video download failed."
            " Ensure the correctness of the link.</b>"
        ),
    }

    strings_ru = {
        "clip_download_started": (
            "<emoji document_id=5307773751796964107>⏳</emoji><b>Скачивание клипа"
            " началось, подождите.</b>"
        ),
        "clip_download_completed": (
            "<b><emoji document_id=5215480011322042129>➡️</emoji>Скачивание клипа"
            " завершено. Отправляю...</b>"
        ),
        "clip_download_failed": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка скачивания"
            " клипа. Убедитесь в ссылке.</b>"
        ),
        "video_download_started": (
            "<b><emoji document_id=5307773751796964107>⏳</emoji>Скачивание видео"
            " началось, подождите.</b>"
        ),
        "video_download_completed": (
            "<b><emoji document_id=5215480011322042129>➡️</emoji>Скачивание видео"
            " завершено. Отправляю...</b>"
        ),
        "video_download_failed": (
            "<b><emoji document_id=5980953710157632545>❌</emoji>Ошибка скачивания"
            " видео. Убедитесь в ссылке.</b>"
        ),
    }

    @loader.command(ru_doc="Скачать клип с Twitch")
    async def twitch(self, message: Message):
        """Download a clip from Twitch"""
        if not (clip_url := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("clip_download_failed"))
            return

        try:
            await utils.answer(message, self.strings("clip_download_started"))

            with youtube_dl.YoutubeDL(
                {
                    "outtmpl": "clip.mp4",
                    "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                }
            ) as ydl:
                ydl.download([clip_url])

            await utils.answer_file(message, "clip.mp4")
        except Exception:
            await utils.answer(message, self.strings("clip_download_failed"))

    @loader.command(ru_doc="Скачать видео с Twitch")
    async def twitchvideo(self, message: Message):
        """Download a video from Twitch"""
        if not (video_url := utils.get_args_raw(message)):
            await utils.answer(message, self.strings("video_download_failed"))
            return

        try:
            await utils.answer(message, self.strings("video_download_started"))

            with youtube_dl.YoutubeDL(
                {
                    "outtmpl": "video.mp4",
                    "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                }
            ) as ydl:
                ydl.download([video_url])

            await utils.answer_file(message, "video.mp4")
        except Exception as e:
            await utils.answer(message, self.strings("video_download_failed"))
