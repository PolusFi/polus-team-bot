from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, CallbackQuery, ChatType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from bson import ObjectId

from tgbot.models.db import Database
from tgbot.filters.user import start_join_callback, start_org_member
from tgbot.states.user import MeetingAbsenceStatesGroup
import tgbot.keyboards as keyboards

db = Database()
db.create()


async def user_start_pm(message: Message):
    #kbd = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Test web", web_app=WebAppInfo(url="https://biswap.org")))
    check_user = db.getDocs(
        database='polus',
        collection='user',
        search={
            'telegram_id': str(message.from_user.id)
        })
    if len(check_user) == 0:
        user = {
            'telegram_id': str(message.from_user.id),
            'username': message.from_user.username,
            'name': message.from_user.first_name,
            'status': 'user',
        }
        db.addDoc(database='polus', collection='user', document=user)
        reply_message = f'Приветствую тебя, {message.from_user.first_name}!\n\n' \
                        f'Выбери одну из опций в меню...'
    else:
        reply_message = f'Привет, {message.from_user.first_name}!\n\n' \
                        f'Выбери одну из опций в меню...'
    user_doc = db.getDoc(database='polus', collection='user', search={'telegram_id': str(message.from_user.id)})
    await message.answer(reply_message, reply_markup=keyboards.inline.user_start(user_doc))


async def user_meetings(callback_query: CallbackQuery, callback_data: dict):
    if callback_data.get('value') == 'all':
        meetings_list = db.getDocs(database='polus', collection='meetings', search={"status": True})
        meetings = "📅 <strong>БЛИЖАЙШИЕ ТИМ МИТЫ POLUS</strong> 📅\n\n"
    elif callback_data.get('value') == 'my':
        meetings_list = db.getDocs(database='polus', collection='meetings', search={
            "status": True,
            "members": str(callback_query.from_user.id)
        })
        meetings = "📅 <strong>ВАШИ БЛИЖАЙШИЕ МИТЫ POLUS</strong> 📅\n\n"

    for meeting in meetings_list:

        members = []
        for member in db.getDocs(database='polus', collection='user',
                                 search={"telegram_id": {"$in": meeting['members']}}):
            members.append(f'@{member["username"]}')
        members = "\n".join(members)

        meetings += f'📄 Name: {meeting["name"]}\n\n' \
                    f'📈 Object: {meeting["goal"]}\n\n' \
                    f'📆 Date: {meeting["date"].strftime("%d/%m/%Y")}\n' \
                    f'⏰ Time: {meeting["time"]}\n\n' \
                    f'👥 Members: \n{members}\n' \
                    f'------------------------------\n\n'

        await callback_query.message.edit_text(meetings)
        await callback_query.message.edit_reply_markup(keyboards.inline.user_back("start"))


async def user_cancel(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    if callback_data.get('value') == 'meeting_absence':
        await state.finish()
        await callback_query.message.delete()


async def user_teem_member_request(callback_query: CallbackQuery, callback_data: dict):
    await callback_query.bot.send_message(chat_id=1247306694,
                           text=f'@{callback_query.from_user.username} wants to join Polus organization',
                           reply_markup=keyboards.inline.admin_org_request(str(callback_query.from_user.id)))


async def user_back(callback_query: CallbackQuery, callback_data: dict):
    user_doc = db.getDoc(
        database='polus',
        collection='user',
        search={
            'telegram_id': str(callback_query.from_user.id)
        })
    if callback_data.get('value') == 'start':
        reply_message = f'Привет, {callback_query.from_user.first_name}!\n\n' \
                        f'Выбери одну из опций в меню...'

        await callback_query.message.edit_text(reply_message)
        await callback_query.message.edit_reply_markup(keyboards.inline.user_start(user_doc))


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start_pm, ChatTypeFilter(chat_type=ChatType.PRIVATE), commands=["start"], state="*")
    dp.register_callback_query_handler(user_teem_member_request, start_join_callback.filter(action="join"))
    dp.register_callback_query_handler(user_back, start_org_member.filter(action="back"))
    dp.register_callback_query_handler(user_cancel, ChatTypeFilter(chat_type=ChatType.PRIVATE),
                                       start_org_member.filter(action='cancel'),
                                       state=MeetingAbsenceStatesGroup.text)
    dp.register_callback_query_handler(user_cancel, ChatTypeFilter(chat_type=ChatType.PRIVATE),
                                       start_org_member.filter(action='meeting_absence'),
                                       state=MeetingAbsenceStatesGroup.text)
    dp.register_callback_query_handler(user_meetings, start_org_member.filter(action="meetings"))


