from aiogram.fsm.state import StatesGroup, State

class AddProductFlow(StatesGroup):
    waiting_for_name = State()