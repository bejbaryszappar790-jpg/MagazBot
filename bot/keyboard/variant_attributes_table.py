from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.enums import ChangingVariantAttribute


def create_variant_attribute_table():

    builder = InlineKeyboardBuilder()

    builder.button(text = "Имя варианта", callback_data = ChangingVariantAttribute.VARIANT_NAME)
    builder.button(text = "Цена варианта", callback_data = ChangingVariantAttribute.VARIANT_PRICE)
    builder.button(text = "Количество варианта", callback_data = ChangingVariantAttribute.VARIANT_QUANTITY)

    builder.button(text = "Вернуться к предыдущему действию", callback_data = "cancel_step")
    builder.button(text = "Отменить полное действие", callback_data = "cancel_action")
        
    builder.adjust(2)

    return builder.as_markup()