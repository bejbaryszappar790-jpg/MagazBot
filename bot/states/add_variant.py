from aiogram.fsm.state import State, StatesGroup


class AddVariantFlow(StatesGroup):
    waiting_for_parent_name = State()
    waiting_for_parent_id = State()
    waiting_for_variant_name = State()
    waiting_for_price = State()
    waiting_for_quantity = State()