from aiogram.dispatcher.filters.state import State, StatesGroup


class MeetingStatesGroup(StatesGroup):
    message_id = State()
    time = State()  # Will be represented in storage as 'Form:time'
    date = State()
    name = State()  # Will be represented in storage as 'Form:name'
    goal = State()
    member = State()  # Will be represented in storage as 'Form:member'


class ProjectStatesGroup(StatesGroup):
    message_id = State()
    name = State()
    softline = State()
    deadline = State()
    member = State()
