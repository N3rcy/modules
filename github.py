
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
from hikkatl.types import Message
from .. import loader, utils


@loader.tds
class GitHubMod(loader.Module):
    """Module for fetching GitHub profile or repository information"""
    strings = {
        "name": "GitHubMod",
        "profile_info": "<b>GitHub Profile Info: </b>",
        "repo_info": "<b>GitHub Repository Info: </b>",
        "invalid_link": "<b><emoji document_id=5978859389614821335>❌</emoji>Invalid GitHub link. The correct link should start with https://github.com...</b>",
        "user_not_found": "<b><emoji document_id=5978859389614821335>❌</emoji>User not found.</b>",
        "repo_not_found": "<b><emoji document_id=5978859389614821335>❌</emoji>Repository not found.</b>"
    }

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    @loader.command(en_doc="fetch information about GitHub profile")
    async def gitprof(self, m: Message):
        """fetch information about GitHub profile"""
        link = utils.get_args_raw(m)
        if not link:
            await utils.answer(m, self.strings["invalid_link"])
            return

        if link.startswith("https://github.com/"):
            parts = link.split("/")
            if len(parts) >= 3:
                username = parts[3]
                api_url = f"https://api.github.com/users/{username}"
                response = requests.get(api_url)
                if response.status_code == 200:
                    user_data = response.json()
                    info_text = f"{self.strings['profile_info']}\n\n" \
                                f"<b><emoji document_id=5224371968014299199>📦</emoji>Link:</b> {link}\n" \
                                f"<b><emoji document_id=5222465715499446573>🌐</emoji>Username:</b> {user_data.get('login', 'N/A')}\n" \
                                f"<b><emoji document_id=5222465715499446573>🌐</emoji>Name:</b> {user_data.get('name', 'N/A')}\n" \
                                f"<b><emoji document_id=5222030772751314651>🖌</emoji>Bio:</b> {user_data.get('bio', 'N/A')}\n" \
                                f"<b><emoji document_id=5221924764368515209>🪧</emoji>Location:</b> {user_data.get('location', 'N/A')}\n" \
                                f"<b><emoji document_id=5222473609649337576>🔥</emoji>Followers:</b> {user_data.get('followers', 'N/A')}\n" \
                                f"<b><emoji document_id=5221962650275034448>❤️</emoji>Following:</b> {user_data.get('following', 'N/A')}\n" \
                                f"<b><emoji document_id=5222341131383091841>📗</emoji>Public Repositories:</b> {user_data.get('public_repos', 'N/A')}\n"
                    avatar_url = user_data.get('avatar_url')
                    if avatar_url:
                        await self.client.send_file(
                            m.chat_id,
                            avatar_url,
                            caption=info_text,
                            link_preview=False,
                            force_document=False
                        )
                        await m.delete()
                    else:
                        await m.delete()
                        await utils.answer(m, info_text)
                else:
                    await utils.answer(m, self.strings["user_not_found"])
            else:
                await utils.answer(m, self.strings["invalid_link"])
        else:
            await utils.answer(m, self.strings["invalid_link"])

    @loader.command(ru_doc="fetch information about GitHub repository")
    async def gitrepo(self, m: Message):
        """fetch information about GitHub repository"""
        link = utils.get_args_raw(m)
        if not link:
            await utils.answer(m, self.strings["invalid_link"])
            return

        if link.startswith("https://github.com/"):
            parts = link.split("/")
            if len(parts) >= 5:
                username = parts[3]
                repo_name = parts[4]
                api_url = f"https://api.github.com/repos/{username}/{repo_name}"
                response = requests.get(api_url)
                if response.status_code == 200:
                    repo_data = response.json()
                    info_text = f"{self.strings['repo_info']}\n\n" \
                                f"<b><emoji document_id=5224371968014299199>📦</emoji>Link:</b> {link}\n" \
                                f"<b><emoji document_id=5222341131383091841>📗</emoji>Repository:</b> {repo_data.get('name', 'N/A')}\n" \
                                f"<b><emoji document_id=5222030772751314651>🖌</emoji>Description:</b> {repo_data.get('description', 'N/A')}\n" \
                                f"<b><emoji document_id=5222465715499446573>🌐</emoji>Language:</b> {repo_data.get('language', 'N/A')}\n" \
                                f"<b><emoji document_id=5222473609649337576>🔥</emoji>Stars:</b> {repo_data.get('stargazers_count', 'N/A')}\n" \
                                f"<b><emoji document_id=5222331261548246439>↕️</emoji>Forks:</b> {repo_data.get('forks_count', 'N/A')}\n" \
                                f"<b><emoji document_id=5334704798765686555>👀</emoji>Watchers:</b> {repo_data.get('watchers_count', 'N/A')}\n"
                    avatar_url = repo_data.get('owner', {}).get('avatar_url')
                    if avatar_url:
                        await self.client.send_file(
                            m.chat_id,
                            avatar_url,
                            caption=info_text,
                            link_preview=False,
                            force_document=False
                        )
                        await m.delete()
                    else:
                        await m.delete()
                        await utils.answer(m, info_text)
                else:
                    await utils.answer(m, self.strings["repo_not_found"])
            else:
                await utils.answer(m, self.strings["invalid_link"])
        else:
            await utils.answer(m, self.strings["invalid_link"])
