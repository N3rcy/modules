#    ╔╗╔┌─┐┬─┐┌─┐┬ ┬
#    ║║║├┤ ├┬┘│  └┬┘
#    ╝╚╝└─┘┴└─└─┘ ┴

# Code is licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# https://creativecommons.org/licenses/by-nc-nd/4.0/
# You CANNOT edit this file without direct permission from the author.
# You can redistribute this file without any changes.

# meta developer: @nercymods
# reqires: feedparser
# scope: hikka_min 1.6.2

import feedparser
from hikkatl.tl.types import Message

from .. import loader, utils

NEWS_SOURCES = {
    "Playground": "https://www.playground.ru/rss/news.xml",
    "BBC": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Le Monde": "https://www.lemonde.fr/rss/une.xml",
    "RIA": "https://ria.ru/export/rss2/archive/index.xml",
    "Lenta": "https://lenta.ru/rss/news",
    "RBC": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
}


@loader.tds
class NewsMod(loader.Module):
    """Module for displaying news from various sources"""

    strings = {"name": "NewsMod"}

    @loader.command(ru_doc="Получить последние новости с Playground")
    async def playground(self, m: Message):
        """Get the latest news from Playground"""
        await self._get_news_from_source(m, "Playground")

    @loader.command(ru_doc="Получить последние новости с BBC")
    async def bbc(self, m: Message):
        """Get the latest news from BBC"""
        await self._get_news_from_source(m, "BBC")

    @loader.command(ru_doc="Получить последние новости с CNN")
    async def cnn(self, m: Message):
        """Get the latest news from CNN"""
        await self._get_news_from_source(m, "CNN")

    @loader.command(ru_doc="Получить последние новости с The Guardian")
    async def guardian(self, m: Message):
        """Get the latest news from The Guardian"""
        await self._get_news_from_source(m, "The Guardian")

    @loader.command(ru_doc="Получить последние новости с Le Monde")
    async def lemonde(self, m: Message):
        """Get the latest news from Le Monde"""
        await self._get_news_from_source(m, "Le Monde")

    @loader.command(ru_doc="Получить последние новости с Риа новости")
    async def ria(self, m: Message):
        """Get the latest news from RIA"""
        await self._get_news_from_source(m, "RIA")

    @loader.command(ru_doc="Получить последние новости с Рбк новости")
    async def rbc(self, m: Message):
        """Get the latest news from rbc"""
        await self._get_news_from_source(m, "RBC")

    @loader.command(ru_doc="Получить последние новости с Lenta")
    async def lenta(self, m: Message):
        """Get the latest news from lenta"""
        await self._get_news_from_source(m, "Lenta")

    async def _get_news_from_source(self, message: Message, source_name: str):
        """Helper method to get news from a specific source"""
        if source_name not in NEWS_SOURCES:
            await utils.answer(
                message, f"Invalid news source: {utils.escape_html(source_name)}"
            )
            return

        feed_url = NEWS_SOURCES[source_name]
        feed = feedparser.parse(feed_url)

        await utils.answer(
            message,
            "<b><emoji document_id=5433982607035474385>📰</emoji>Latest 15 news from"
            f" {source_name}</b>:\n\n"
            + "\n\n".join(
                f"{i+1}: <a href='{entry.link}'>{utils.escape_html(entry.title)}</a>"
                for i, entry in enumerate(feed.entries[:15])
            ),
        )
