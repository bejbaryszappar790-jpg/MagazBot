from aiogram.fsm.state import State, StatesGroup


class UpdateVariantFlow(StatesGroup):
    waiting_for_parent_name = State()
    waiting_for_parent_id = State()
    waiting_for_variant_id = State()
    waiting_for_variant_attributes = State()
    waiting_for_new_data = State()