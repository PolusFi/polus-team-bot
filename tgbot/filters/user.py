from aiogram.utils.callback_data import CallbackData

start_join_callback = CallbackData("start", "action", "user")

start_org_member = CallbackData("polus", "action", "value", "user")

default_user_callback = CallbackData("user", "location", "action", "value", "user")

meeting_callback = CallbackData("meeting", "action", "value")
