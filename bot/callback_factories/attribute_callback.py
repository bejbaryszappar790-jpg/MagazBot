from aiogram.filters.callback_data import CallbackData


class AttributeCallback(CallbackData, prefix = "attribute"):
    callback_type : str
    attribute_type : str