from aiogram.dispatcher.filters.state import State, StatesGroup


class MeetingAbsenceStatesGroup(StatesGroup):
    meeting_id = State()
    text = State()
