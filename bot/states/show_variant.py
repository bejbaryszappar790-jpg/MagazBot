from aiogram.fsm.state import StatesGroup, State

class ShowVariantFlow(StatesGroup):
    waiting_for_parent_name = State()
    waiting_for_parent_id = State()
    waiting_for_variant_id = State()
    