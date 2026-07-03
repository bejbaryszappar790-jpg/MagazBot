from aiogram.fsm.state import StatesGroup, State

class AddVariantFlow(StatesGroup):
    waiting_for_parent_name = State()
    waiting_for_parent_id = State()
    waiting_variant_name = State()
    waiting_for_price = State()
    waiting_for_quantity = State()