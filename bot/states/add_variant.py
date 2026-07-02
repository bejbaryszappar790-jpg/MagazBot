from aiogram.fsm.state import StatesGroup, State

class AddVariantFlow(StatesGroup):
    waiting_for_attributes = State()
    waiting_for_price = State()
    waiting_for_quantity = State()