from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.item_callback import ItemCallback


def create_item_table_buttons(data : dict, action : str):
    builder = InlineKeyboardBuilder()

    for key, value in data.items():
        builder.button(text = f"{key}", callback_data = ItemCallback(action = action, item_id = value))


    builder.button(text = "Вернуться к предыдущему действию", callback_data = "cancel_step")
    builder.button(text = "Отменить полное действие", callback_data = "cancel_action")

    builder.adjust(2)
    
    return builder.as_markup()