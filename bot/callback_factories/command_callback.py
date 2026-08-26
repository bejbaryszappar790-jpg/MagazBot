from aiogram.filters.callback_data import CallbackData


class CommandCallback(CallbackData, prefix = "command"):
    action : str
    type : str