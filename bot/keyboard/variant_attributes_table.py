from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callback_factories.attribute_callback import AttributeCallback
from bot.callback_factories.command_callback import CommandCallback
from bot.enums import ChangingVariantAttribute, RegressButtonText, RegressButtonType

attribute = "attribute"

def create_variant_attribute_table():

    builder = InlineKeyboardBuilder()

    builder.button(text = "Имя варианта", callback_data = AttributeCallback(callback_type = attribute, attribute_type = ChangingVariantAttribute.VARIANT_NAME))
    builder.button(text = "Цена варианта", callback_data = AttributeCallback(callback_type = attribute, attribute_type = ChangingVariantAttribute.VARIANT_PRICE))
    builder.button(text = "Количество варианта", callback_data = AttributeCallback(callback_type = attribute, attribute_type = ChangingVariantAttribute.VARIANT_QUANTITY))

    builder.button(text = RegressButtonText.GO_BACK, callback_data = CommandCallback(action = "/update_variant", type = RegressButtonType.GO_BACK))
    builder.button(text = RegressButtonText.CANCEL, callback_data = CommandCallback(action = "/update_variant", type = RegressButtonType.CANCEL))
    
        
    builder.adjust(2)

    return builder.as_markup()