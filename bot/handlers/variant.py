import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_factories.item_callback import ItemCallback
from bot.enums import OperationMode, ThingType
from bot.keyboard.item_table import create_item_table_buttons
from bot.schemas.products.getparentidforgetvariant import GetParentIdForGetVariant
from bot.schemas.products.getproductidforvariant import GetProductIdForVariant
from bot.schemas.products.getproductnameforvariant import GetProductNameForVariant
from bot.schemas.users.verifyuser import VerifyUser
from bot.schemas.variants.getvariantname import GetVariantName
from bot.schemas.variants.getvariantprice import GetVariantPrice
from bot.schemas.variants.getvarianttoshow import GetVariantToShow
from bot.schemas.variants.receivingvarquantity import ReceivingVarQuantity
from bot.services.user_services import UserService
from bot.services.variant_services import VariantService
from bot.states.add_variant import AddVariantFlow
from bot.states.show_variant import ShowVariantFlow
from bot.tools.helper import validate_user_input
from bot.errors.server_error import ServerAbsenceError

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

    
    

@router.message(Command("show_variant"))
async def start_showing_variant(message : Message, state : FSMContext):
    if message.from_user is None:
        logger.warning("Неизвестный пользователь без телеграм id пытался увидеть вариант.")
        await message.answer(
            "Вы не зарегестрированы."
        )
        await state.clear()
        return

    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} успешно начал команду /show_variant.")
    await message.answer(
        "Теперь напишите имя продукта чьей вариант хотите увидеть!"
    )
    await state.update_data(user_id = message.from_user.id)
    await state.set_state(ShowVariantFlow.waiting_for_parent_name)



@router.message(ShowVariantFlow.waiting_for_parent_name)
async def get_parent_name_to_show_variant(message : Message, variant_service : VariantService, state : FSMContext):

    state_data = await state.get_data()

    data = {
            "parent_name" : message.text,
            "mode" : OperationMode.READ,
            **state_data
        }
    service_args = validate_user_input(schema = GetProductNameForVariant, data = data, user_id = state_data.get("user_id"), validated_data = "parent_name")
    product_data = await variant_service.get_product_name_for_variant(id = service_args.user_id, parent_name = service_args.parent_name, mode = service_args.mode)

    product_kb = create_item_table_buttons(data = product_data, action = "/show_variant")

    await message.answer(
        "Теперь выберите продукт чей варианты вы хотите увидеть.",
        reply_markup = product_kb
    )

    await state.update_data(parent_name = message.text)
    await state.set_state(ShowVariantFlow.waiting_for_parent_id)


@router.callback_query(ShowVariantFlow.waiting_for_parent_id,
                       ItemCallback.filter(F.action == "/show_variant")
                       )
async def get_parent_id_to_show_variant(callback : CallbackQuery, 
                                        variant_service : VariantService,
                                        callback_data : ItemCallback,
                                        state : FSMContext
                                        ):
    if callback.data is None or callback.message is None:
            await callback.answer("Что то пошло не так.", show_alert = False)
            await state.clear()
            return
    
    
    state_data = await state.get_data()
    

    data = {
            "parent_id" : callback_data.item_id,
            **state_data
    }
    service_args = GetParentIdForGetVariant(**data)
    variant_data = await variant_service.get_parent_id_for_get_variant(parent_name = service_args.parent_name,
                                                                        parent_id = service_args.parent_id,
                                                                        user_id = service_args.user_id
                                                                        )

    await callback.answer()
    variant_kb = create_item_table_buttons(data = variant_data, action = "/show_variant")
    await state.update_data(parent_id = service_args.parent_id)
    await state.set_state(ShowVariantFlow.waiting_for_variant_id)
    
    await callback.message.answer(
        "Теперь выберите вариянт продукта чьи данные вы хотите увидеть.",
        reply_markup = variant_kb
    )
    

@router.callback_query(
    ShowVariantFlow.waiting_for_variant_id,
    ItemCallback.filter(F.action == "/show_variant")
)
async def finish_showing_variant(callback : CallbackQuery, 
                                 callback_data : ItemCallback,
                                 variant_service : VariantService, 
                                 state : FSMContext):

    
    if callback.data is None or callback.message is None:
            await callback.answer("Что то пошло не так.", show_alert = False)
            await state.clear()
            return
    
    await callback.answer()
    state_data = await state.get_data()
    

    data = {
            **state_data,
            "variant_id" : callback_data.item_id
        }
    service_args = GetVariantToShow(**data)

    found_variant = await variant_service.get_variant_to_show(parent_id = service_args.parent_id,
                                                                parent_name = service_args.parent_name,
                                                                variant_id = service_args.variant_id,
                                                                user_id = service_args.user_id
                                                                )
    await callback.message.answer(
        f"Продукт: {service_args.parent_name}\nВариант: {found_variant.var_name}\nЦена варианта: {found_variant.var_price}\nКоличество варианта {found_variant.var_quantity}"
    )

    await state.clear()
    