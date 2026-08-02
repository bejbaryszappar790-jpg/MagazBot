from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def create_item_table_buttons(data : dict):
    builder = InlineKeyboardBuilder()

    for key, value in data.items():
        builder.add(InlineKeyboardButton(text = f"{key}", callback_data = f"item_{value}"))

    
    builder.adjust(2)
    
    return builder.as_markup()