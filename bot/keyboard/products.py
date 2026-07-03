from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def create_product_buttons(data : dict):
    builder = InlineKeyboardBuilder()

    for key, value in data.items():
        builder.add(InlineKeyboardButton(text = f"{key}", callback_data = "product_{value}"))

    
    builder.adjust(1)
    
    return builder.as_markup()