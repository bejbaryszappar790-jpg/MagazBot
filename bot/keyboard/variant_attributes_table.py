from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.enums import ChangingVariantAttribute


def create_variant_attribute_table():

    builder = InlineKeyboardBuilder()

    builder.button(text = "Имя варианта", callback_data = ChangingVariantAttribute.VARIANT_NAME)
    builder.button(text = "Цена варианта", callback_data = ChangingVariantAttribute.VARIANT_PRICE)
    builder.button(text = "Количество варианта", callback_data = ChangingVariantAttribute.VARIANT_QUANTITY)

    builder.adjust(2)

    return builder.as_markup()