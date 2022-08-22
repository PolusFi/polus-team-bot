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
import tgbot.keyboards as keyboards

db = Database()
db.create()


async def user_meeting_checkin_pm(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):

    # TODO : If user already submitted -> hide buttons or else ...

    meeting_doc = db.getDoc(database='polus',
                            collection='meetings',
                            search={"status": True, "_id": ObjectId(callback_data.get('value'))})

    if callback_data.get('action') == 'dis_checkin':

        await MeetingAbsenceStatesGroup.text.set()
        async with state.proxy() as data:
            data['meeting_id'] = callback_data.get('value')

        await callback_query.bot.send_message(chat_id=callback_query.from_user.id,
                                              text=f'✏️ Опишите причину вашего отсутствия',
                                              reply_markup=keyboards.inline.user_cancel("meeting_absence"))

    elif callback_data.get('action') == 'checkin':

        meeting_doc['checkin'].append(str(callback_query.from_user.id))

        await callback_query.bot.send_message(chat_id=callback_query.from_user.id,
                                              text=f'✅ Отлично, до встречи на митапе!')
        await callback_query.message.edit_reply_markup(keyboards.inline.remove_keyboard())

    db.updateDoc(database='polus', collection='meetings', search={'_id': meeting_doc['_id']}, update_doc=meeting_doc)


async def user_meeting_checkin(callback_query: CallbackQuery, callback_data: dict):
    meeting_doc = db.getDoc(database='polus',
                            collection='meetings',
                            search={"status": True, "_id": ObjectId(callback_data.get('value'))})

    if str(callback_query.from_user.id) not in meeting_doc['checkin']:

        meeting_doc['checkin'].append(str(callback_query.from_user.id))
        text = callback_query.message.text + f'\n@{callback_query.from_user.username}'
        db.updateDoc(database='polus', collection='meetings', search={'_id': meeting_doc['_id']}, update_doc=meeting_doc)

        await callback_query.message.edit_text(text)
        await callback_query.message.edit_reply_markup(keyboards.inline.meeting_checkin(meeting_doc))


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


def register_meeting(dp: Dispatcher):
    dp.register_message_handler(user_meeting_absence_pm, ChatTypeFilter(chat_type=ChatType.PRIVATE),
                                state=MeetingAbsenceStatesGroup.text)
    dp.register_callback_query_handler(user_meeting_checkin_pm, ChatTypeFilter(chat_type=ChatType.PRIVATE),
                                       meeting_callback.filter())
    dp.register_callback_query_handler(user_meeting_checkin, meeting_callback.filter(action="checkin"))
