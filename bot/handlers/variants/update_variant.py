import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.callback_factories.item_callback import ItemCallback
from aiogram.fsm.context import FSMContext
from bot.errors.client_error import UnknownUserError
from bot.schemas.users.verifyuser import VerifyUser
from bot.services.user_services import UserService
from bot.enums import ThingType
from bot.states.update_variant import UpdateVariantFlow
from bot.services.product_services import ProductService
from bot.enums import OperationMode
from bot.tools.helper import validate_user_input
from bot.schemas.products.getproductnameforvariant import GetProductNameForVariant
from bot.services.variant_services import VariantService
from bot.keyboard.item_table import create_item_table_buttons
from bot.errors.server_error import ServerAbsenceError
from bot.schemas.variants.returnvarianttable import ReturnVariantTableSchema
from bot.schemas.variants.getvarianttoshow import GetVariantToShow
from bot.keyboard.variant_attributes_table import create_variant_attribute_table


router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("update_variant"))
async def start_update_variant_handler(message : Message, user_servcie : UserService, state : FSMContext):
    if message.from_user is None:
        raise UnknownUserError("Вы не авторизованы!", "Неизвестный пользователь пыталься использовать команду /update_variant.", clear_state = True)


    service_args = VerifyUser(user_id = message.from_user.id)

    result = await user_servcie.verify_user(admin_id = service_args.user_id, thing_type = ThingType.VARIANT)

    if result:
        await message.answer(
            "Напишите имя продукта чей вариант вы хотите изменить."
        )
        await state.update_data(admin_id = message.from_user.id)
        await state.set_state(UpdateVariantFlow.waiting_for_parent_name)

        
@router.message(UpdateVariantFlow.waiting_for_parent_name)
async def receinving_parent_name_for_update_variant(message : Message, variant_services : VariantService, state : FSMContext):

    if not message.text:
        await message.answer(
            "Вы ничего не написали!"
        )
        return
    state_data = await state.get_data()


    data = {
        "user_id" : state_data.get("admin_id"),
        "parent_name" : message.text,
        "mode" : OperationMode.WRITE
    }

    service_args = validate_user_input(schema = GetProductNameForVariant, data = data, user_id = state_data.get("admin_id"), validated_data = "parent_name")

    product_data = await variant_services.get_product_name_for_variant(id = service_args.user_id, parent_name = service_args.parent_name, mode = service_args.mode)

    kb = create_item_table_buttons(data = product_data, action = "/update_variant")

    await state.set_state(UpdateVariantFlow.waiting_for_parent_id)
    await message.answer(
        "Выберите продукт чей вариант вы хотите изменить.",
        reply_markup = kb
    )
    return

@router.callback_query(UpdateVariantFlow.waiting_for_parent_id,
                       ItemCallback.filter(F.action == "/update_variant")
                       )
async def receive_parent_id_for_update_variant(callback : CallbackQuery, 
                                               callback_data : ItemCallback,
                                               variant_service : VariantService,
                                               state : FSMContext
                                               ):
    if callback.message is None:
        raise ServerAbsenceError("Обьект message нету внутри CallbackQuery в хэндлере receive_parent_id_for_update_variant")

    state_data = await state.get_data()

    data = {
        "parent_id" : callback_data.item_id,
        "user_id" : state_data.get("admin_id"),
        **state_data
    }
    service_args = ReturnVariantTableSchema(**data)
    existing_product = await variant_service.get_product_id_for_variant(parent_id = service_args.parent_id, admin_id = service_args.user_id)
    variant_data = await variant_service.return_variant_table(parent_id = service_args.parent_id, user_id = service_args.user_id, parent_name = existing_product.parent_name)

    kb = create_item_table_buttons(data = variant_data, action = "/update_variant")

    await callback.message.answer(
        "Теперь выберите тот вариант которого вы хотите изменить.",
        reply_markup = kb
    )
    await state.update_data(parent_id = service_args.parent_id)
    await state.update_data(parent_id = service_args.parent_name)
    await state.set_state(UpdateVariantFlow.waiting_for_variant_id)

@router.callback_query(
    UpdateVariantFlow.waiting_for_variant_id,
    ItemCallback.filter(F.action == "/update_variant")
)
async def receive_variant_id_to_show_var_attribute(
    callback : CallbackQuery,
    callback_data : ItemCallback,
    variant_service : VariantService,
    state : FSMContext

):
    if callback.message is None:
        raise ServerAbsenceError("Обьект message нету внутри CallbackQuery в хэндлере receive_parent_id_for_update_variant")


    state_data = await state.get_data()

    data = {
        "variant_id" : callback_data.item_id,
        "user_id" : state_data.get("admin_id"),
        **state_data
    }

    service_args = GetVariantToShow(**data)

    existing_variant = await variant_service.get_variant_to_show(parent_name = service_args.parent_name,
                                                            parent_id = service_args.parent_id,
                                                           variant_id = service_args.variant_id,
                                                           user_id = service_args.user_id
                                                            )
    kb = create_variant_attribute_table()

    await callback.message.answer(
        "Выберите какой аттрибут варианта вы хотите изменить.",
        reply_markup = kb
    )
    await state.update_data(variant_id = existing_variant.var_id)
    await state.set_state(UpdateVariantFlow.waiting_for_variant_attributes)



@router.callback_query(
    UpdateVariantFlow.waiting_for_variant_attributes
)
async def receive_var_attribute_to_update(
    callback : CallbackQuery,
    variant_service : VariantService,
    state : FSMContext
):

    if callback.message is None:
        raise ServerAbsenceError("Обьект message нету внутри CallbackQuery в хэндлере receive_parent_id_for_update_variant")

    
    
    