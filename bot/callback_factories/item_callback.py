from aiogram.filters.callback_data import CallbackData


class ItemCallback(CallbackData, prefix = "item"):
    action : str
    item_id : int