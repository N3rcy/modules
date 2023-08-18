__version__ = (1, 1, 0)

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
from deep_translator import GoogleTranslator
from hikkatl.tl.types import Message

from .. import loader, utils

languages = ["ru", "en", "ja"]


@loader.tds
class JikanModule(loader.Module):
    """Module for working with Jikan API"""

    strings = {
        "name": "JikanModule",
        "anime_not_found": "<b>No anime found.</b>",
        "character_not_found": "<b>No character found.</b>",
        "manga_not_found": "<b>No manga found.</b>",
        "expression_missing": "<b>Please specify a search query.</b>",
        "result": "<b>Result:</b>\n{result}",
        "error": "<b>Error:</b> {error}",
    }
    strings_ru = {
        "anime_not_found": "<b>Аниме не найдено.</b>",
        "character_not_found": "<b>Персонаж не найден.</b>",
        "manga_not_found": "<b>Манга не найдена.</b>",
        "expression_missing": "<b>Пожалуйста, укажите поисковой запрос.</b>",
        "result": "<b>Результат:</b>\n{result}",
        "error": "<b>Ошибка:</b> {error}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "language",
                "en",
                lambda: "Language of output",
                validator=loader.validators.Choice(languages),
            ),
        )

    @loader.command(
        ru_doc="Поиск аниме по названию",
        en_doc="Search for anime by title",
    )
    async def sanime(self, message: Message):
        """Search for anime by title"""
        query = utils.get_args_raw(message)

        if not query:
            await utils.answer(message, self.strings["expression_missing"])
            return

        translator = GoogleTranslator(source="auto", target="en")
        tquery = translator.translate(query)
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/anime",
            params={"q": tquery},
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            await utils.answer(message, self.strings["anime_not_found"])
            return

        anime = data["data"][0]

        title = anime.get("title")
        title_english = anime.get("title_english")
        title_japanese = anime.get("title_japanese")
        type_ = anime.get("type")
        episodes = anime.get("episodes")
        status = anime.get("status")
        start_date = anime.get("aired").get("from") if "aired" in anime else None
        end_date = anime.get("aired").get("to") if "aired" in anime else None
        duration = anime.get("duration")
        rating = anime.get("rating")
        score = anime.get("score")
        synopsis = anime.get("synopsis")
        sfw = anime.get("sfw") is None

        result = f"<b>Title:</b> {title}\n"
        if title_english:
            result += f"<b>English Title:</b> {title_english}\n"
        if title_japanese:
            result += f"<b>Japanese Title:</b> {title_japanese}\n"
        if type_:
            result += f"<b>Type:</b> {type_}\n"
        if episodes:
            result += f"<b>Episodes:</b> {episodes}\n"
        if status:
            result += f"<b>Status:</b> {status}\n"
        if start_date:
            start_date = start_date.split("T")[0]
            result += f"<b>Start Date:</b> {start_date}\n"
        if end_date:
            end_date = end_date.split("T")[0]
            result += f"<b>End Date:</b> {end_date}\n"
        if duration:
            result += f"<b>Duration:</b> {duration}\n"
        if rating:
            result += f"<b>Rating:</b> {rating}\n"
        if score:
            result += f"<b>Score:</b> {score}\n"
        if sfw:
            result += f"<b>SFW:</b> Yes\n"
        else:
            result += f"<b>SFW:</b> No\n"
        if synopsis:
            result += f"<b>Synopsis:</b> {synopsis}"

        if self.config["language"] == "en":
            await utils.answer(message, self.strings["result"].format(result=result))
        else:
            translator = GoogleTranslator(source="auto", target=self.config["language"])
            translation = translator.translate(
                self.strings["result"].format(result=result)
            )
            await utils.answer(message, translation)

    @loader.command(ru_doc="Поиск манги по названию", en_doc="Search manga by title")
    async def smanga(self, m: Message):
        """Search manga by title"""
        query = utils.get_args_raw(m)

        if not query:
            await utils.answer(m, self.strings["expression_missing"])
            return

        translator = GoogleTranslator(source="auto", target="en")
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/manga",
            params={"q": query},
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            await utils.answer(m, self.strings["manga_not_found"])
            return

        manga = data["data"][0]

        title = manga.get("title")
        title_english = manga.get("title_english")
        title_japanese = manga.get("title_japanese")
        type_ = manga.get("type")
        chapters = manga.get("chapters")
        volumes = manga.get("volumes")
        status = manga.get("status")
        start_date = (
            manga.get("published").get("from") if "published" in manga else None
        )
        end_date = manga.get("published").get("to") if "published" in manga else None
        score = manga.get("score")
        synopsis = manga.get("synopsis")
        sfw = manga.get("explicit_genres") is None

        result = f"<b>Title:</b> {title}\n"
        if title_english:
            result += f"<b>English Title:</b> {title_english}\n"
        if title_japanese:
            result += f"<b>Japanese Title:</b> {title_japanese}\n"
        if type_:
            result += f"<b>Type:</b> {type_}\n"
        if chapters:
            result += f"<b>Chapters:</b> {chapters}\n"
        if volumes:
            result += f"<b>Volumes:</b> {volumes}\n"
        if status:
            result += f"<b>Status:</b> {status}\n"
        if start_date:
            start_date = start_date.split("T")[0]
            result += f"<b>Start Date:</b> {start_date}\n"
        if end_date:
            end_date = end_date.split("T")[0]
            result += f"<b>End Date:</b> {end_date}\n"
        if score:
            result += f"<b>Score:</b> {score}\n"
        if sfw:
            result += f"<b>SFW:</b> Yes\n"
        else:
            result += f"<b>SFW:</b> No\n"
        if synopsis:
            result += f"<b>Synopsis:</b> {synopsis}"

        if self.config["language"] == "en":
            await utils.answer(m, self.strings["result"].format(result=result))
            return

        translator = GoogleTranslator(source="auto", target=self.config["language"])
        translation = translator.translate(self.strings["result"].format(result=result))
        await utils.answer(m, translation)

    @loader.command(
        ru_doc="Поиск персонажа по имени",
        en_doc="Search character by name",
    )
    async def scharacter(self, message: Message):
        """Search character by name"""
        query = utils.get_args_raw(message)

        if not query:
            await utils.answer(message, self.strings["expression_missing"])
            return

        translator = GoogleTranslator(source="auto", target="en")
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/characters",
            params={"q": query},
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            await utils.answer(message, self.strings["character_not_found"])
            return

        character = data["data"][0]

        name = character.get("name")
        name_kanji = character.get("name_kanji")
        nicknames = character.get("nicknames")
        favorites = character.get("favorites")
        about = character.get("about")

        result = f"<b>Name:</b> {name}\n"
        if name_kanji:
            result += f"<b>Kanji Name:</b> {name_kanji}\n"
        if nicknames:
            result += f"<b>Nicknames:</b> {', '.join(nicknames)}\n"
        if favorites is not None:
            result += f"<b>Favorites:</b> {favorites}\n"
        if about:
            result += f"<b>About:</b> {about}"

        if self.config["language"] == "en":
            await utils.answer(message, self.strings["result"].format(result=result))
            return

        translator = GoogleTranslator(source="auto", target=self.config["language"])
        translation = translator.translate(self.strings["result"].format(result=result))
        await utils.answer(message, translation)

    @loader.command(
        ru_doc="Получить рекомендации аниме",
        en_doc="Get anime recommendations",
    )
    async def rсanime(self, message: Message):
        """Get anime recommendations"""
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/recommendations/anime",
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            await utils.answer(
                message,
                self.strings["error"].format(error="No recommendations found."),
            )
            return

        recommendations = data["data"][:3]

        result = ""
        for recommendation in recommendations:
            title = recommendation["entry"][0].get("title")
            content = recommendation.get("content")
            user = recommendation.get("user")
            username = user.get("username") if user else None

            result += f"<b>Title:</b> {title}\n" if title else ""
            result += f"<b>Content:</b> {content}\n" if content else ""
            result += f"<b>User:</b> {username}\n" if username else ""
            result += "\n"

        if self.config["language"] == "en":
            await utils.answer(message, self.strings["result"].format(result=result))
            return

        translator = GoogleTranslator(source="auto", target=self.config["language"])
        translation = translator.translate(self.strings["result"].format(result=result))
        await utils.answer(message, translation)

    @loader.command(
        ru_doc="Получить рекомендации манги",
        en_doc="Get manga recommendations",
    )
    async def rсmanga(self, message: Message):
        """Get manga recommendations"""
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/recommendations/manga",
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            await utils.answer(
                message,
                self.strings["error"].format(error="No recommendations found."),
            )
            return

        recommendations = data["data"][:3]

        result = ""
        for recommendation in recommendations:
            title = recommendation["entry"][0].get("title")
            content = recommendation.get("content")
            user = recommendation.get("user")
            username = user.get("username") if user else None

            result += f"<b>Title:</b> {title}\n" if title else ""
            result += f"<b>Content:</b> {content}\n" if content else ""
            result += f"<b>User:</b> {username}\n" if username else ""
            result += "\n"

        if self.config["language"] == "en":
            await utils.answer(message, self.strings["result"].format(result=result))
            return

        translator = GoogleTranslator(source="auto", target=self.config["language"])
        translation = translator.translate(self.strings["result"].format(result=result))
        await utils.answer(message, translation)

    @loader.command(ru_doc="Случайное аниме", en_doc="Random anime")
    async def ranime(self, message: Message):
        """Random anime"""
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/random/anime",
        )
        data = response.json()

        if not data.get("data"):
            await utils.answer(message, self.strings["anime_not_found"])
            return

        anime = data["data"]

        title = anime.get("title")
        title_english = anime.get("title_english")
        title_japanese = anime.get("title_japanese")
        type_ = anime.get("type")
        episodes = anime.get("episodes")
        status = anime.get("status")
        airing = anime.get("airing")
        duration = anime.get("duration")
        rating = anime.get("rating")
        score = anime.get("score")
        synopsis = anime.get("synopsis")

        result = f"<b>Title:</b> {title}\n"
        if title_english:
            result += f"<b>English Title:</b> {title_english}\n"
        if title_japanese:
            result += f"<b>Japanese Title:</b> {title_japanese}\n"
        if type_:
            result += f"<b>Type:</b> {type_}\n"
        if episodes:
            result += f"<b>Episodes:</b> {episodes}\n"
        if status:
            result += f"<b>Status:</b> {status}\n"
        if airing is not None:
            result += f"<b>Airing:</b> {airing}\n"
        if duration:
            result += f"<b>Duration:</b> {duration}\n"
        if rating:
            result += f"<b>Rating:</b> {rating}\n"
        if score:
            result += f"<b>Score:</b> {score}\n"
        if synopsis:
            result += f"<b>Synopsis:</b> {synopsis}"

        if self.config["language"] == "en":
            await utils.answer(message, self.strings["result"].format(result=result))
            return

        translator = GoogleTranslator(source="auto", target=self.config["language"])
        translation = translator.translate(self.strings["result"].format(result=result))
        await utils.answer(message, translation)

    @loader.command(ru_doc="Случайная манга", en_doc="Random manga")
    async def rmanga(self, message: Message):
        """Random manga"""
        response = await utils.run_sync(
            requests.get,
            "https://api.jikan.moe/v4/random/manga",
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            await utils.answer(message, self.strings["manga_not_found"])
            return

        anime = data["data"]

        title = anime.get("title")
        title_english = anime.get("title_english")
        title_japanese = anime.get("title_japanese")
        type_ = anime.get("type")
        episodes = anime.get("episodes")
        status = anime.get("status")
        airing = anime.get("airing")
        duration = anime.get("duration")
        rating = anime.get("rating")
        score = anime.get("score")
        synopsis = anime.get("synopsis")

        result = f"<b>Title:</b> {title}\n"
        if title_english:
            result += f"<b>English Title:</b> {title_english}\n"
        if title_japanese:
            result += f"<b>Japanese Title:</b> {title_japanese}\n"
        if type_:
            result += f"<b>Type:</b> {type_}\n"
        if episodes:
            result += f"<b>Episodes:</b> {episodes}\n"
        if status:
            result += f"<b>Status:</b> {status}\n"
        if airing is not None:
            result += f"<b>Airing:</b> {airing}\n"
        if duration:
            result += f"<b>Duration:</b> {duration}\n"
        if rating:
            result += f"<b>Rating:</b> {rating}\n"
        if score:
            result += f"<b>Score:</b> {score}\n"
        if synopsis:
            result += f"<b>Synopsis:</b> {synopsis}"

        if self.config["language"] == "en":
            await utils.answer(message, self.strings["result"].format(result=result))
            return

        translator = GoogleTranslator(source="auto", target=self.config["language"])
        translation = translator.translate(self.strings["result"].format(result=result))
        await utils.answer(message, translation)
