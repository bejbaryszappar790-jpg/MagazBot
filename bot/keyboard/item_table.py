from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.command_callback import CommandCallback
from bot.callback_factories.item_callback import ItemCallback
from bot.enums import RegressButtonType


def create_item_table_buttons(data : dict, action : str,):
    builder = InlineKeyboardBuilder()

    for key, value in data.items():
        builder.button(text = f"{key}", callback_data = ItemCallback(action = action, item_id = value))


    builder.button(text = "Назад", callback_data = CommandCallback(action = action, type = RegressButtonType.GO_BACK))
    builder.button(text = "Отменить полное действие", callback_data = CommandCallback(action = action, type = RegressButtonType.CANCEL))

    builder.adjust(2)
    
    return builder.as_markup()