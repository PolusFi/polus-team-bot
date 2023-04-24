from aiogram import Dispatcher, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, CallbackQuery, ChatType
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from bson import ObjectId

from tgbot.models.db import Database
from tgbot.filters.user import meeting_callback
from tgbot.states.user import MeetingAbsenceStatesGroup
from tgbot.filters.admin import admin_action_callback, admin_back_callback
import tgbot.keyboards as keyboards

db = Database()
db.create()


def format_meeting_text(meeting_doc: dict):
    members = []
    for member in db.getDocs(
            database='polus',
            collection='user',
            search={"telegram_id": {"$in": meeting_doc['members']}}
    ):
        members.append(
            f'@{member["username"]} ' + (
                '✅' if member['telegram_id'] in meeting_doc['checkin'] else (
                    '❌' if member['telegram_id'] in meeting_doc['absent'].keys() else '➖'
                )
            )
        )

    hour = meeting_doc["time"].split(":")[0]
    minute = meeting_doc["time"].split(":")[1]

    members = "\n".join(members)

    meeting = f'📄 Name: {meeting_doc["name"]}\n\n' \
              f'📈 Object: {meeting_doc["goal"]}\n\n' \
              f'📆 Date: {meeting_doc["date"].strftime("%d/%m/%Y")}\n' \
              f'⏰ Time:\n' \
              f'Istanbul: {hour}:{minute} ({hour % 12}:{minute} {"PM" if hour > 12 else "AM"})\n' \
              f'Kyiv: {int(hour)}:{minute} ({hour % 12}:{minute} {"PM" if hour > 12 else "AM"})\n' \
              f'Batumi: {int(hour)+1}:{minute} ({(hour+1) % 12}:{minute} {"PM" if (hour+1) > 12 else "AM"})\n' \
              f'Almaty: {int(hour)+3}:{minute} ({(hour+3) % 12}:{minute} {"PM" if (hour+3) > 12 else "AM"})\n' \
              f'EST: {int(hour)-8}:{minute} ({(int(hour)-8) % 12}:{minute} {"PM" if (hour-8) > 12 else "AM"})\n\n'
              f'👥 Members: \n{members}'

    return meeting


async def user_meeting_checkin_pm(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):

    meeting_doc = db.getDoc(database='polus',
                            collection='meetings',
                            search={"status": True, "_id": ObjectId(callback_data.get('value'))})
    
    if meeting_doc and str(callback_query.from_user.id) not in meeting_doc['checkin'] and \
       str(callback_query.from_user.id) not in meeting_doc['absent'].keys():

        if callback_data.get('action') == 'dis_checkin':

            await MeetingAbsenceStatesGroup.text.set()
            async with state.proxy() as data:
                data['meeting_id'] = callback_data.get('value')

            await callback_query.bot.send_message(
                chat_id=callback_query.from_user.id,
                text=f'✏️ Опишите причину вашего отсутствия',
                reply_markup=keyboards.inline.user_cancel("meeting_absence")
            )

        elif callback_data.get('action') == 'checkin':

            meeting_doc['checkin'].append(str(callback_query.from_user.id))

            await callback_query.bot.send_message(
                chat_id=callback_query.from_user.id,
                text=f'✅ Отлично, до встречи на митапе!'
            )
            await callback_query.message.edit_reply_markup(keyboards.inline.remove_keyboard())

        db.updateDoc(
            database='polus',
            collection='meetings',
            search={'_id': meeting_doc['_id']},
            update_doc=meeting_doc
        )

        try:
            meeting_text = format_meeting_text(meeting_doc=meeting_doc)
            await callback_query.bot.edit_message_text(
                text=meeting_text,
                chat_id=callback_query.bot['config'].tg_bot.dev_chat,
                message_id=meeting_doc['pinned_msg_id'],
                reply_markup=keyboards.inline.meeting_checkin(meeting_doc)
            )
        except(Exception) as e:
            print(e)

    else:
        await callback_query.message.edit_reply_markup(keyboards.inline.remove_keyboard())
    await callback_query.answer(show_alert=True)


async def user_meeting_checkin(callback_query: CallbackQuery, callback_data: dict):
    meeting_doc = db.getDoc(
        database='polus',
        collection='meetings',
        search={
            "status": True,
            "_id": ObjectId(callback_data.get('value'))
        }
    )



    if meeting_doc and \
       str(callback_query.from_user.id) not in meeting_doc['checkin'] and \
       str(callback_query.from_user.id) in meeting_doc['members']:

        meeting_doc['checkin'].append(str(callback_query.from_user.id))
        db.updateDoc(
            database='polus',
            collection='meetings',
            search={'_id': meeting_doc['_id']},
            update_doc=meeting_doc
        )

    try:
        meeting = format_meeting_text(meeting_doc=meeting_doc)

        await callback_query.message.edit_text(meeting)
        await callback_query.message.edit_reply_markup(keyboards.inline.meeting_checkin(meeting_doc))
    except(Exception) as e:
        print(e)

    await callback_query.answer(show_alert=True)


async def user_meeting_absence_pm(message: Message, state: FSMContext):
    async with state.proxy() as data:

        data['text'] = message.text
        meeting_doc = db.getDoc(database='polus',
                                collection='meetings',
                                search={"status": True, "_id": ObjectId(data['meeting_id'])})
        meeting_doc['absent'][str(message.from_user.id)] = message.text
        db.updateDoc(database='polus',
                     collection='meetings',
                     search={'_id': ObjectId(data['meeting_id'])},
                     update_doc=meeting_doc)

    await state.finish()
    await message.bot.edit_message_text(
        text=f'Спасибо что сообщили, в этот раз обойдемся без увольнения, но впредь будьте аккуратнее!',
        chat_id=message.from_user.id,
        message_id=message.message_id - 1
    )


async def end_meeting(callback_query: CallbackQuery, callback_data: dict):

    meeting_doc = db.getDoc(
        database='polus',
        collection='meetings',
        search={
            '_id': ObjectId(callback_data.get('value'))
        }

    )
    meeting_doc['status'] = False

    db.updateDoc(database='polus',
                 collection='meetings',
                 search={'_id': ObjectId(callback_data.get('value'))},
                 update_doc=meeting_doc)

    meeting_docs = db.getDocs(database='polus', collection='meetings', search={}, order_by={'date': 0})
    try:
        await callback_query.bot.unpin_chat_message(chat_id=callback_query.bot['config'].tg_bot.dev_chat,
                                                    message_id=meeting_doc['pinned_msg_id'])
    except(Exception) as e:
        print(e)
    await callback_query.message.edit_text("Recent POLUS team meetings")
    await callback_query.message.edit_reply_markup(keyboards.inline.admin_meetings(meeting_docs))


def register_meeting(dp: Dispatcher):
    dp.register_message_handler(user_meeting_absence_pm, ChatTypeFilter(chat_type=ChatType.PRIVATE),
                                state=MeetingAbsenceStatesGroup.text)
    dp.register_callback_query_handler(user_meeting_checkin_pm, ChatTypeFilter(chat_type=ChatType.PRIVATE),
                                       meeting_callback.filter())
    dp.register_callback_query_handler(user_meeting_checkin, meeting_callback.filter(action="checkin"))
    dp.register_callback_query_handler(end_meeting, admin_action_callback.filter(action="end_meeting"), is_admin=True)
