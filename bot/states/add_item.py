from aiogram.fsm.state import StatesGroup, State

class AddItemFlow(StatesGroup):
    waiting_for_name = State()
    waiting_for_attributes = State()
    waiting_for_quantity = State()