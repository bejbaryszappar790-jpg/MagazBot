from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.enums import ChangingVariantAttribute, RegressButtonText, RegressButtonType


def create_variant_attribute_table():

    builder = InlineKeyboardBuilder()

    builder.button(text = "Имя варианта", callback_data = ChangingVariantAttribute.VARIANT_NAME)
    builder.button(text = "Цена варианта", callback_data = ChangingVariantAttribute.VARIANT_PRICE)
    builder.button(text = "Количество варианта", callback_data = ChangingVariantAttribute.VARIANT_QUANTITY)

    builder.button(text = RegressButtonText.GO_BACK, callback_data = RegressButtonType.GO_BACK)
    builder.button(text = RegressButtonText.CANCEL, callback_data = RegressButtonType.CANCEL)
    
        
    builder.adjust(2)

    return builder.as_markup()