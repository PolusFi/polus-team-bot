from aiogram import Dispatcher
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

from tgbot.models.db import Database

db = Database()
db.create()

async def group_meetings(query: InlineQuery):
    print(query)
    #kbd = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Test web", web_app=WebAppInfo(url="https://biswap.org")))
    user_doc = db.getDoc(database='polus',
                         collection='user',
                         search={
                             'telegram_id': str(query.from_user.id),
                             'status': {'$in': ['member', 'founder', 'owner', 'admin']}
                         })
    if user_doc != None:
        meetings = "📅 <strong>Ближайшие сходки подписчиков POLUS</strong> 📅\n\n"
        my_meetings = "📅 <strong>Мои сходки POLUS</strong> 📅\n\n"
        for meeting in db.getDocs(database='polus', collection='meetings', search={"status": True}):
            members = []
            for member in db.getDocs(database='polus', collection='user',
                                     search={"telegram_id": {"$in": meeting['members']}}):
                members.append(f'@{member["username"]}')
            members = "\n".join(members)

            if str(query.from_user.id) in meeting['members']:
                my_meetings += f'📄 Name: {meeting["name"]}\n\n' \
                               f'📈 Object: {meeting["goal"]}\n\n' \
                               f'📆 Date: {meeting["date"].strftime("%d/%m/%Y")}\n' \
                               f'⏰ Time: {meeting["time"]}\n\n' \
                               f'------------------------------\n\n'

            meetings += f'📄 Name: {meeting["name"]}\n\n' \
                        f'📈 Object: {meeting["goal"]}\n\n' \
                        f'📆 Date: {meeting["date"].strftime("%d/%m/%Y")}\n' \
                        f'⏰ Time: {meeting["time"]}\n\n' \
                        f'👥 Members: \n{members}\n' \
                        f'------------------------------\n\n'
        await query.answer(
            results=[
                InlineQueryResultArticle(
                    id="0",
                    title="Polus teem meetings",
                    input_message_content=InputTextMessageContent(
                        message_text=meetings
                    ),
                    thumb_url="https://ipfs.io/ipfs/bafkreigooinxs7ytpbspg47kl5vit6lkw7zjoirtrtdmfnmhnge32drwey"
                ),
                InlineQueryResultArticle(
                    id="1",
                    title="My teem meetings",
                    input_message_content=InputTextMessageContent(
                        message_text=my_meetings,
                    ),
                    thumb_url="https://ipfs.io/ipfs/bafkreigooinxs7ytpbspg47kl5vit6lkw7zjoirtrtdmfnmhnge32drwey"
                )
            ],
            cache_time=5
        )

def register_group(dp: Dispatcher):
    dp.register_inline_handler(group_meetings, text="")