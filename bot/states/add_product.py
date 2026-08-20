from aiogram.fsm.state import State, StatesGroup


class AddProductFlow(StatesGroup):
    waiting_for_name = State()