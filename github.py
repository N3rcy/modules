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
from hikkatl.tl.types import Message

from .. import loader, utils


@loader.tds
class GitHubMod(loader.Module):
    """Module for fetching GitHub profile or repository information"""

    strings = {
        "name": "GitHubMod",
        "profile_info": "<b>GitHub Profile Info: </b>",
        "repo_info": "<b>GitHub Repository Info: </b>",
        "invalid_link": (
            "<b><emoji document_id=5978859389614821335>❌</emoji>Invalid GitHub link."
            " The correct link should start with https://github.com...</b>"
        ),
        "user_not_found": (
            "<b><emoji document_id=5978859389614821335>❌</emoji>User not found.</b>"
        ),
        "repo_not_found": (
            "<b><emoji document_id=5978859389614821335>❌</emoji>Repository not"
            " found.</b>"
        ),
    }

    @loader.command(en_doc="<profile / url> - Fetch information about GitHub profile")
    async def gitprof(self, message: Message):
        """<profile / url> - Fetch information about GitHub profile"""
        if not (link := utils.get_args_raw(message)):
            await utils.answer(message, self.strings["invalid_link"])
            return

        if link.startswith("https://github.com/"):
            username = link.split("/")[3]

        try:
            response = await utils.run_sync(
                requests.get, f"https://api.github.com/users/{username}"
            )
            response.raise_for_status()
            user_data = response.json()
            info_text = (
                f"{self.strings['profile_info']}\n\n<b><emoji"
                " document_id=5224371968014299199>📦</emoji>Link:</b>"
                f" {link}\n<b><emoji"
                " document_id=5222465715499446573>🌐</emoji>Username:</b>"
                f" {user_data.get('login', 'N/A')}\n<b><emoji"
                " document_id=5222465715499446573>🌐</emoji>Name:</b>"
                f" {user_data.get('name', 'N/A')}\n<b><emoji"
                " document_id=5222030772751314651>🖌</emoji>Bio:</b>"
                f" {user_data.get('bio', 'N/A')}\n<b><emoji"
                " document_id=5221924764368515209>🪧</emoji>Location:</b>"
                f" {user_data.get('location', 'N/A')}\n<b><emoji"
                " document_id=5222473609649337576>🔥</emoji>Followers:</b>"
                f" {user_data.get('followers', 'N/A')}\n<b><emoji"
                " document_id=5221962650275034448>❤️</emoji>Following:</b>"
                f" {user_data.get('following', 'N/A')}\n<b><emoji"
                " document_id=5222341131383091841>📗</emoji>Public Repositories:</b>"
                f" {user_data.get('public_repos', 'N/A')}\n"
            )

            if avatar_url := user_data.get("avatar_url"):
                await utils.answer_file(
                    message,
                    avatar_url,
                    info_text,
                    link_preview=False,
                )
            else:
                await utils.answer(message, info_text)
        except Exception:
            await utils.answer(message, self.strings["user_not_found"])

    @loader.command(ru_doc="Fetch information about GitHub repository")
    async def gitrepo(self, message: Message):
        """Fetch information about GitHub repository"""
        if not (link := utils.get_args_raw(message)):
            await utils.answer(message, self.strings["invalid_link"])
            return

        if link.startswith("https://github.com/"):
            parts = link.split("/")
            if len(parts) >= 5:
                username = parts[3]
                repo_name = parts[4]
        elif len(link.split("/")) == 2:
            username, repo_name = link.split("/")

        try:
            response = await utils.run_sync(
                requests.get, f"https://api.github.com/repos/{username}/{repo_name}"
            )
            response.raise_for_status()
            repo_data = response.json()
            info_text = (
                f"{self.strings['repo_info']}\n\n<b><emoji"
                " document_id=5224371968014299199>📦</emoji>Link:</b>"
                f" {link}\n<b><emoji"
                " document_id=5222341131383091841>📗</emoji>Repository:</b>"
                f" {repo_data.get('name', 'N/A')}\n<b><emoji"
                " document_id=5222030772751314651>🖌</emoji>Description:</b>"
                f" {repo_data.get('description', 'N/A')}\n<b><emoji"
                " document_id=5222465715499446573>🌐</emoji>Language:</b>"
                f" {repo_data.get('language', 'N/A')}\n<b><emoji"
                " document_id=5222473609649337576>🔥</emoji>Stars:</b>"
                f" {repo_data.get('stargazers_count', 'N/A')}\n<b><emoji"
                " document_id=5222331261548246439>↕️</emoji>Forks:</b>"
                f" {repo_data.get('forks_count', 'N/A')}\n<b><emoji"
                " document_id=5334704798765686555>👀</emoji>Watchers:</b>"
                f" {repo_data.get('watchers_count', 'N/A')}\n"
            )
            if avatar_url := repo_data.get("avatar_url"):
                await utils.answer_file(
                    message,
                    avatar_url,
                    info_text,
                    link_preview=False,
                )
            else:
                await utils.answer(message, info_text)
        except Exception:
            await utils.answer(message, self.strings["repo_not_found"])
