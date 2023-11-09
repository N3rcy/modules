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

from collections import defaultdict
import matplotlib.pyplot as plt
import io

@loader.tds
class Top(loader.Module):
    """Module for viewing the top list in chat"""
    strings = {"name": "Top",
        "top": "Top users by message count",
        "topchat": "<emoji document_id=5323538339062628165>💬</emoji><b> Top users in</b>",
        "msgcount": "Message count",
        "loading": "<emoji document_id=5780543148782522693>🕒</emoji><b> Message counting has started, please wait, it may take a long time if there are a lot of messages in the chat</b>",
    }

    strings_ru = {
        "top": "Топ пользователей по количеству сообщений",
        "topchat": "<emoji document_id=5323538339062628165>💬</emoji><b> Топ пользователей в</b>",
        "msgcount": "Количество сообщений",
        "loading": "<emoji document_id=5780543148782522693>🕒</emoji><b> Подсчет сообщений начался, пожалуйста подождите, это может занять много времени если в чате много сообщений</b>",
    }


    @loader.command(ru_doc="Посмотреть топ в чате")
    async def top(self, m: Message):
        "View top in the chat"

        await utils.answer(m, self.strings['loading'])

        client = self.client
        chat_id = m.chat.id 

        message_count = defaultdict(int)
            
        async for message in client.iter_messages(chat_id):
            if message.sender_id:
                message_count[message.sender_id] += 1

        users = await client.get_participants(chat_id)
        users_dict = {user.id: (user.username or user.first_name) for user in users}

        message_count = {user_id: count for user_id, count in message_count.items() if user_id in users_dict}

        sorted_message_count = sorted(message_count.items(), key=lambda item: item[1], reverse=True)[:20]

        # Create a list of usernames and counts for the top 20 users
        usernames = [users_dict[user_id] for user_id, count in sorted_message_count]
        counts = [count for user_id, count in sorted_message_count]

        # Plot the data
        plt.figure(figsize=(10, 5))
        plt.barh(usernames, counts, color='skyblue')
        plt.xlabel(self.strings['msgcount'])
        plt.title(self.strings['top'])
        plt.gca().invert_yaxis()

        # Save the plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Create a mini top for the caption
        top_users = [(users_dict[user_id], count) for user_id, count in sorted_message_count]
        caption = f"{self.strings['topchat']} <b>{m.chat.title}:</b>\n" + "\n".join([f'"{user}" - {count}' for user, count in top_users])

        # Send the image
        await utils.answer_file(m, buf, caption, force_document=False)

