import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_factories.item_callback import ItemCallback
from bot.enums import OperationMode, ThingType, UserRole
from bot.errors.server_error import ServerAbsenceError
from bot.keyboard.item_table import create_item_table_buttons
from bot.schemas.products.getproductidforvariant import GetProductIdForVariant
from bot.schemas.products.getproductnameforvariant import GetProductNameForVariant
from bot.schemas.users.verifyuser import VerifyUser
from bot.schemas.variants.getvariantname import GetVariantName
from bot.schemas.variants.getvariantprice import GetVariantPrice
from bot.schemas.variants.receivingvarquantity import ReceivingVarQuantity
from bot.services.user_services import UserService
from bot.services.variant_services import VariantService
from bot.states.add_variant import AddVariantFlow
from bot.utils.helper import validate_user_input

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("add_variant"))
async def check_parent_name(message : Message,  
                            user_service : UserService,
                            state : FSMContext
                            ):
    if message.from_user is None:
        await message.answer(
            "Id пользователя не найден"
        )
        await state.clear()
        return
    


    service_args = VerifyUser(user_id = message.from_user.id)
    result = await user_service.verify_user(admin_id = service_args.user_id,
                                            thing_type = ThingType.VARIANT
                                                            )
    if result:
        await state.set_state(AddVariantFlow.waiting_for_parent_name)
        await state.update_data(admin_id = message.from_user.id)
        await state.update_data(user_role = UserRole.ADMIN)
        await state.update_data(action = "/add_variant")
        await message.answer(
            "Отправьте имя продукта к которому хотите добавить вариант."
        )
        return
    
    await message.answer(
        "Ошибка сервера"
    )
    logger.error("Метод start_creating_variant в сервисе вариянта вернула False.")
    await state.clear()
    
    


@router.message(AddVariantFlow.waiting_for_parent_name
                )
async def receiving_parent_name(message : Message, 
                                variant_service : VariantService,
                                state : FSMContext
                                ):

    if message.from_user is None:
            await message.answer("Ошибка сервера.")
            logger.error("message.from_user пустой.")
            await state.clear()
            return
    
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
    service_args = validate_user_input(GetProductNameForVariant, data = data, user_id = state_data.get("admin_id"), validated_data = "parent_name")
    product_data = await variant_service.get_product_name_for_variant(parent_name = service_args.parent_name, 
                                                                    id = service_args.user_id,
                                                                    mode = service_args.mode
                                                    )
    
    if product_data:
        kb = create_item_table_buttons(data = product_data, action = "/add_variant")
        await state.update_data(input_name = message.text)
        await state.update_data(mode = service_args.mode)
        await state.set_state(AddVariantFlow.waiting_for_parent_id)
        await message.answer(
            "Выберите продукт которому хотите добавить вариант.",
            reply_markup = kb
        )
        return
    await message.answer(
        "Почему то product_data пуст."
    )
    await state.clear()
    

@router.callback_query(
    AddVariantFlow.waiting_for_parent_id,
    ItemCallback.filter(F.action == "/add_variant")
    )
async def receiving_parent_id(callback : CallbackQuery, 
                              variant_service : VariantService, 
                              callback_data : ItemCallback,
                              state : FSMContext
                              ):
    
    if callback.data is None or callback.message is None:
        await callback.answer("Что то пошло не так.", show_alert = False)
        await state.clear()
        return
    
    await callback.answer()

    state_data = await state.get_data()

    if not state_data:
        raise ServerAbsenceError("Мы не получили словарь от FSMContext в хэндлере receiving_parent_id.")

    
    data = {
        "parent_id" : callback_data.item_id,
        **state_data
    }
    service_args = GetProductIdForVariant(**data)
    result = await variant_service.get_product_id_for_variant(parent_id = service_args.parent_id,
                                                        admin_id = service_args.admin_id
                                                        )

    await state.update_data(parent_id = result.parent_id)
    await state.update_data(parent_name = result.parent_name)
    await state.set_state(AddVariantFlow.waiting_for_variant_name)

    await callback.message.answer(
        "Напишите имя варианта которую вы хотите добавить."
        )
    


@router.message(AddVariantFlow.waiting_for_variant_name)
async def receiving_var_name(message : Message, variant_service : VariantService, state : FSMContext):
    if not message.text: 
        await message.answer(
            "Напишите имя варианта!"
        )
        return
    
    state_data = await state.get_data()

    data = {
        "variant_name" : message.text,
        **state_data
    }
    service_args = validate_user_input(schema = GetVariantName, data = data, user_id = state_data.get("admin_id"), validated_data = "variant_name")
    result = await variant_service.get_variant_name(variant_name = service_args.variant_name, 
                                                parent_id = service_args.parent_id,
                                                admin_id = service_args.admin_id
                                                )
    if result:
        
        await state.update_data(variant_name = message.text)

        await state.set_state(AddVariantFlow.waiting_for_price)
        await message.answer(
            "Теперь напишите цену варианта."
        )
        return
    await message.answer(
        "Ошибка: Почему то result получисля False"
    )
    



@router.message(AddVariantFlow.waiting_for_price)
async def receiving_var_price(message : Message, 
                              variant_service : VariantService,
                              state : FSMContext):
    
    

    
    if message.text is None:
        await message.answer(
            "Вы не написали цену!"
        )
        return

    state_data = await state.get_data()

    data = {
        "input_price" : message.text,
        **state_data
    }
    service_args = validate_user_input(schema = GetVariantPrice, data = data, user_id = state_data.get("admin_id"), validated_data = "variant_price")

    variant_price = variant_service.get_variant_price(
        input_price = service_args.input_price,
        admin_id = service_args.admin_id
                                                        )
    
    if variant_price is not None:
        await state.update_data(variant_price = variant_price)
        await state.set_state(AddVariantFlow.waiting_for_quantity)
        await message.answer(
            "Теперь напишите количество варианта."
        )
        return
    
    await message.answer(
        "Почему из сервиса вариянта и из метода .get_VariantPrice не вернулся цена."
    )
    
        
@router.message(AddVariantFlow.waiting_for_quantity)
async def receiving_var_quantity(message : Message, 
                                 variant_service : VariantService, 
                                 state : FSMContext):

    
    
    if not message.text:
        await message.answer(
            "Вы не отправили количество"
        )
        return
    
    state_data = await state.get_data()

    data = {
        "quantity" : message.text,
        **state_data
    }

    service_args = validate_user_input(schema = ReceivingVarQuantity, data = data, user_id = state_data.get("admin_id"), validated_data = "variant_quantity")
    
    new_variant = await variant_service.finish_creating_variant(quantity = service_args.quantity,
                                                                parent_id = service_args.parent_id,
                                                                var_name = service_args.variant_name,
                                                                var_price = service_args.variant_price,
                                                                admin_id = service_args.admin_id
                                                                )
    
    if new_variant:
        logger.info(f"Пользователь {service_args.admin_id} создал вариант {service_args.variant_name} продукта с id {service_args.parent_id}")
        await message.answer(
            f"Вариянт по имени {service_args.variant_name} успешно создался"
        )
        
    else:
        logger.error(f"Пользователь {service_args.admin_id} не смог создать вариант {service_args.variant_name} продукта {service_args.parent_id}")
        await message.answer(
            "Ошибка сервера."
        )
    
    await state.clear()
