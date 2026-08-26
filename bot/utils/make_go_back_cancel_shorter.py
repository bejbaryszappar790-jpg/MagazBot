from bot.enums import ThingType, UserRole
from bot.errors.server_error import ServerMissingDataError
from bot.keyboard.item_table import create_item_table_buttons
from bot.schemas.products.getproductnameforvariant import GetProductNameForVariant
from bot.schemas.variants.returnvarianttable import ReturnVariantTableSchema
from bot.services.variant_services import VariantService
from bot.utils.helper import validate_user_input


async def make_go_back_cancel_shorter(variant_service : VariantService, state_data : dict, table : ThingType):
    parent_name = state_data.get("parent_name")
    parent_id = state_data.get("parent_id")
    user_role = state_data.get("user_role")
    action = state_data.get("action")
    if user_role is UserRole.ADMIN:
        id = state_data.get("admin_id")
    else:
        id = state_data.get("user_id")


    if (not parent_name or parent_id is None or not user_role or not action or id is None):
        raise ServerMissingDataError("Данные не полные для создание кнопок в роутере callback_go_back_cancel_handler")

    
    if table is ThingType.VARIANT:
        data = {
            "parent_id" : parent_id,
            "user_id" : id
        }

        service_args = ReturnVariantTableSchema(**data)
        existing_product = await variant_service.get_product_id_for_variant(parent_id = parent_id, admin_id = service_args.user_id)
        data_for_table = await variant_service.return_variant_table(parent_name = existing_product.parent_name, parent_id = existing_product.parent_id, user_id = id)
        
    else:
        mode = state_data.get("mode")
        if mode is None:
            raise ServerMissingDataError("Переменная mode пуст в хэндлере allback_go_back_cancel_handler")
            
        data = {
            "user_id" : id,
            "parent_name" : parent_name,
            "mode" : mode
        }

        service_args = validate_user_input(schema = GetProductNameForVariant, data = data, user_id = id, validated_data = "parent_name")
        data_for_table = await variant_service.get_product_name_for_variant(id = service_args.user_id, parent_name = service_args.parent_name, mode = service_args.mode)


    kb = create_item_table_buttons(data = data_for_table, action = action)
    return kb