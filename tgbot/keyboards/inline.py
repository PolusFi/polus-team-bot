from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from tgbot.filters.user import start_join_callback, start_org_member, default_user_callback, meeting_callback
from tgbot.filters.admin import admin_action_callback, admin_back_callback

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

vote_cb = CallbackData('vote', 'action', 'value')  # post:<action>:<value>

def meeting_checkin(meeting: dict):
    kbd = InlineKeyboardMarkup()
    kbd.add(InlineKeyboardButton(
        text="✅ Буду",
        callback_data=meeting_callback.new(action="checkin", value=meeting['_id'])
    ))
    return kbd

def meeting_checkin_pm(meeting: dict):
    kbd = InlineKeyboardMarkup()
    kbd.add(InlineKeyboardButton(
        text="✅ Буду",
        callback_data=meeting_callback.new(action="checkin", value=meeting['_id'])
    ))
    kbd.add(InlineKeyboardButton(
        text="❌ Не смогу",
        callback_data=meeting_callback.new(action="dis_checkin", value=meeting['_id'])
    ))
    return kbd

def meeting_notify(meetings: list):
    kbd = InlineKeyboardMarkup()
    for meeting in meetings:
        kbd.add(InlineKeyboardButton(
            text=meeting['name'],
            callback_data=admin_action_callback.new(action="notify_group", value=meeting['_id'])
        ))
    return kbd


def meeting_members(members: list):
    kbd = InlineKeyboardMarkup()
    for i in range(0, len(members), 2):
        try:
            kbd.row(
                InlineKeyboardButton(
                    text=f"@{members[i]['username']}",
                    callback_data=str(members[i]['telegram_id'])
                ),
                InlineKeyboardButton(
                    text=f"@{members[i+1]['username']}",
                    callback_data=str(members[i+1]['telegram_id'])
                )
            )
        except:
            kbd.add(
                InlineKeyboardButton(
                    text=f"@{members[i]['username']}",
                    callback_data=str(members[i]['telegram_id'])
                )
            )
    if len(members) != 0:
        kbd.add(InlineKeyboardButton(text=f"All", callback_data='All'))
    kbd.add(InlineKeyboardButton(text=f"End", callback_data='0'))
    return kbd


def admin_start():
    kbd = InlineKeyboardMarkup()
    kbd.row(
        InlineKeyboardButton(
            text=f"Add meeting",
            callback_data=admin_action_callback.new(action="add_meeting", value="0")
        ),
        InlineKeyboardButton(
            text=f"Meetings",
            callback_data=admin_action_callback.new(action="all_meetings", value="0")
        )
    )
    return kbd


def admin_meetings(meetings: list):
    kbd = InlineKeyboardMarkup()
    for meeting in meetings[0:10]:
        kbd.add(
            InlineKeyboardButton(
                text=f"{meeting['name']} ({meeting['date'].strftime('%d/%m/%Y')})",
                callback_data=admin_action_callback.new(action="meeting", value=meeting['_id'])
            )
        )
    kbd.add(InlineKeyboardButton(
                text=f"◀️ Back",
                callback_data=admin_back_callback.new(location="start", value="0")
            ))
    return kbd


def admin_meeting(meeting: dict):
    kbd = InlineKeyboardMarkup()
    kbd.add(InlineKeyboardButton(
        text="Оповестить участников",
        callback_data=admin_action_callback.new(action="notify_group", value=meeting['_id'])
    ))
    kbd.add(
        InlineKeyboardButton(
            text=f"Завершить",
            callback_data=admin_action_callback.new(action="end_meeting", value=meeting['_id'])
        )
    )
    kbd.add(InlineKeyboardButton(
        text=f"◀️ Back",
        callback_data=admin_action_callback.new(action="all_meetings", value="0")
    ))
    return kbd


def admin_org_request(telegram_id: str):
    kbd = InlineKeyboardMarkup()
    kbd.row(
        InlineKeyboardButton(
            text=f"Accept",
            callback_data=start_join_callback.new(action="accept", user=str(telegram_id))
        ),
        InlineKeyboardButton(
            text=f"Discard",
            callback_data=start_join_callback.new(action="discard", user=str(telegram_id))
        )
    )
    return kbd


def user_start(user: dict):
    kbd = InlineKeyboardMarkup()
    if user['status'] == 'member':
        kbd.row(
            InlineKeyboardButton(
                text="📑 Предстоящие митинги",
                callback_data=start_org_member.new(action="meetings", value="all", user=user['telegram_id'])
            ),
            InlineKeyboardButton(
                text="👤 Мои митинги",
                callback_data=start_org_member.new(action="meetings", value="my", user=user['telegram_id'])
            )
        )
    else:
        kbd.add(InlineKeyboardButton(
            text="Я сотрудник Polus",
            callback_data=start_join_callback.new(action="join", user=user['telegram_id']))
        )
    return kbd

def user_back(location: str):
    kbd = InlineKeyboardMarkup()
    kbd.add(InlineKeyboardButton(text="◀️ Назад",
                                 callback_data=start_org_member.new(
                                     action="back",
                                     value=location,
                                     user="0"
                                 ))
            )
    return kbd


def user_cancel(location: str):
    kbd = InlineKeyboardMarkup()
    kbd.add(InlineKeyboardButton(text="❌ Отмена",
                                 callback_data=start_org_member.new(
                                     action="cancel",
                                     value=location,
                                     user="0"
                                 ))
            )
    return kbd


def user_accept_discard(action: str, value: str):
    kbd = InlineKeyboardMarkup()
    kbd.add(InlineKeyboardButton(text="✅ Подтвердить",
                                 callback_data=start_org_member.new(
                                     action=action,
                                     value=value,
                                     user="0"
                                 ))
            )
    kbd.add(InlineKeyboardButton(text="❌ Отмена",
                                 callback_data=start_org_member.new(
                                     action="cancel",
                                     value=value,
                                     user="0"
                                 ))
            )
    return kbd


def remove_keyboard():
    return InlineKeyboardMarkup()