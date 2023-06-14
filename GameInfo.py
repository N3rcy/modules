
#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴ 

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# scope: hikka_min 1.6.2

from hikkatl.types import Message
from .. import loader, utils
import requests

@loader.tds
class GameInfo(loader.Module):
    """Module for fetching game information from RAWG"""
    strings = {
        "name": "GameInfo",
        "game_not_found": "<b>❌ Game not found</b>",
        "fetching": "<b>🌐 Fetching game information...</b>",
        "error_fetching": "<b>❌ Error fetching game information</b>",
        "game": "<b><emoji document_id=5467583879948803288>🎮</emoji>Name: </b>%s",
        "release": "<b><emoji document_id=5431897022456145283>📆</emoji>Data released: </b>%s",
        "rawg_rating": "<b><emoji document_id=5435957248314579621>⭐️</emoji>Rating: </b>%s",
        "platforms": "<b><emoji document_id=5386764531152198851>🏴‍☠️</emoji>Platforms: </b>%s",
        "genres": "<b><emoji document_id=5188705588925702510>🎶</emoji>Genres: </b>%s",
        "screenshots": "<b><emoji document_id=5818849313555483639>📸</emoji>Screenshots: </b>%s"
    }

    strings_ru = {
        "game_not_found": "<b>❌ Игра не найдена</b>",
        "fetching": "<b>🌐 Получение информации об игре...</b>",
        "error_fetching": "<b>❌ Ошибка при получении информации об игре</b>",
        "game": "<b><emoji document_id=5467583879948803288>🎮</emoji>Название: </b>%s",
        "release": "<b><emoji document_id=5431897022456145283>📆</emoji>Дата релиза: </b>%s",
        "rawg_rating": "<b><emoji document_id=5435957248314579621>⭐️</emoji>Рейтинг: </b>%s",
        "platforms": "<b><emoji document_id=5386764531152198851>🏴‍☠️</emoji>Платформы: </b>%s",
        "genres": "<b><emoji document_id=5188705588925702510>🎶</emoji>Жанры: </b>%s",
        "screenshots": "<b><emoji document_id=5818849313555483639>📸</emoji>Скриншоты: </b>%s"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(ru_doc="Получить информацию об игре <название игры>")
    async def gameinfo(self, m: Message):
        """Fetch game information from RAWG"""
        game_name = utils.get_args_raw(m)
        if not game_name:
            await utils.answer(m, self.strings_ru["game_not_found"])
            return

        await utils.answer(m, self.strings_ru["fetching"])

        api_key = "5d26334d8cfc4ede91d0dd9d68d41b85"

        try:
            url = f"https://api.rawg.io/api/games?key={api_key}&search={game_name}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()["results"][0]

                game_name = data.get("name", "N/A")
                released_date = data.get("released", "N/A")
                rating = data.get("rating", "N/A")

                platforms = []
                for platform in data.get("platforms", []):
                    platforms.append(platform["platform"]["name"])
                platforms_str = ", ".join(platforms) if platforms else "N/A"

                genres = []
                for genre in data.get("genres", []):
                    genres.append(genre["name"])
                genres_str = ", ".join(genres) if genres else "N/A"

                screenshots = []
                url = f"https://api.rawg.io/api/games/{data['id']}/screenshots?key={api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    screenshots_data = response.json()["results"][:3]
                    for screenshot in screenshots_data:
                        screenshots.append(screenshot["image"])
                screenshots_str = ", ".join(screenshots) if screenshots else "N/A"

                game_info_message = (
                    self.strings_ru["game"] % game_name + "\n" +
                    self.strings_ru["release"] % released_date + "\n" +
                    self.strings_ru["rawg_rating"] % rating + "\n" +
                    self.strings_ru["platforms"] % platforms_str + "\n" +
                    self.strings_ru["genres"] % genres_str + "\n" +
                    self.strings_ru["screenshots"] % screenshots_str
                )
                await utils.answer(m, game_info_message)
            else:
                await utils.answer(m, self.strings_ru["game_not_found"])
        except Exception:
            await utils.answer(m, self.strings_ru["error_fetching"])
