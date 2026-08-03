import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.states.add_variant import AddVariantFlow
from bot.services.variant_services import VariantService
from bot.services.user_services import UserService
from bot.errors.server_error import (
    ServerError
    )
from bot.errors.client_error import (
    ClientError,
    AbsenceError
)
from bot.keyboard.item_table import create_item_table_buttons
from bot.states.show_variant import ShowVariantFlow
from bot.enums import OperationMode
from bot.callback_factories.item_callback import ItemCallback

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
    

    try:
        result = await user_service.verify_user(admin_id = message.from_user.id
                                                              )
        if result:
            await state.set_state(AddVariantFlow.waiting_for_parent_name)

            await message.answer(
                "Отправьте имя продукта к которому хотите добавить вариант."
            )
            return
        
        await message.answer(
            "Ошибка сервера"
        )
        logger.error("Метод start_creating_variant в сервисе вариянта вернула False.")
        await state.clear()
    except ClientError as e:
        logger.warning(f"{e.log_message}")
        await message.answer(
            f"{e.user_message}"
        )
        await state.clear()

    except ServerError:
        logger.exception("Ошибка в хэндлере который начинает создавать check_parent_name")
        await message.answer(
            "Ошибка сервера"
        )
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
    
    try:
        admin_id = message.from_user.id
        product_data = await variant_service.get_product_name_for_variant(parent_name = message.text, 
                                                                       user_id = admin_id,
                                                                       mode = OperationMode.WRITE
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
    except ClientError as e:
        logger.warning(f"{e.log_message}", exc_info = True)
        await message.answer(
            f"{e.user_message}"
        )

    except ServerError:
        logger.exception("Ошибка в хэндлере receiving_parent_name")
        await message.answer(
            "Ошибка сервера."
        )
        await state.clear()

@router.callback_query(
    AddVariantFlow.waiting_for_parent_id,
    ItemCallback.filter(F.action == "/add_variant")
    )
async def receiving_parent_id(callback : CallbackQuery, 
                              variant_service : VariantService, 
                              state : FSMContext
                              ):

    if callback.from_user is None:
        await callback.answer()
        await callback.message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return
    
    if callback.data is None or callback.message is None:
        await callback.answer("Что то пошло не так.", show_alert = False)
        await state.clear()
        return
    
    await callback.answer()
    admin_id  = callback.from_user.id
    try:
        parent_id = await variant_service.get_product_id_for_variant(text = text,
                                                            admin_id = admin_id
                                                            )
        
        if parent_id:
            await state.update_data(parent_id = parent_id)
            await state.set_state(AddVariantFlow.waiting_for_variant_name)

            await callback.message.answer(
                "Напишите имя варианта которую вы хотите добавить."
            )
            return
        
        await callback.message.answer(
            "Почему то parent_id пуст"
        )
        await state.clear()
    except ClientError as e:
        logger.warning(f"{e.log_message}")
        await callback.message.answer(
            f"Ошибка: {e.user_message}"
        )
        
        await state.clear()
    except ServerError:
        logger.exception("Ошибка в хэндлере receiving_parent_id.")
        await callback.message.answer(
            "Ошибка сервера."
        )
        await state.clear()


@router.message(AddVariantFlow.waiting_for_variant_name)
async def receiving_var_name(message : Message, variant_service : VariantService, state : FSMContext):
    if message.from_user is None:
        await message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return

    
    if not message.text: 
        await message.answer(
            "Напишите имя варианта!"
        )
        return
    

    admin_data = await state.get_data()

    parent_id = admin_data.get("parent_id", None)
    if parent_id is None:
        await message.answer(
            "Мы не смогли получить id продукта."
        )
        await state.clear()
        return

    admin_id = message.from_user.id
    try:
        result = await variant_service.get_variant_name(variant_name = message.text, 
                                                 parent_id = parent_id,
                                                 admin_id = admin_id
                                                 )
        if result:
            
            await state.update_data(var_name = message.text)

            await state.set_state(AddVariantFlow.waiting_for_price)
            await message.answer(
                "Теперь напишите цену варианта."
            )
            return
        await message.answer(
            "Ошибка: Почему то result получисля False"
        )

    except ClientError as e:
        logger.warning(f"{e.log_message}", exc_info = True)
        await message.answer(
            f"{e.user_message}"
        )

    except ServerError:
        logger.exception("Ошибка в хэндлере receiving_var_name")
        await message.answer(
            "Ошибка сервера."
        )
        await state.clear()

@router.message(AddVariantFlow.waiting_for_price)
async def receiving_var_price(message : Message, 
                              variant_service : VariantService,
                              state : FSMContext):

    if message.from_user is None:
        await message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return

    
    if message.text is None:
        await message.answer(
            "Вы не написали цену!"
        )
        return
    
    admin_id = message.from_user.id

    try:
        variant_price = variant_service.get_variant_price(
            input_price = message.text,
            admin_id = admin_id
                                                         )
        
        if variant_price is not None:
            await state.update_data(var_price = variant_price)
            await state.set_state(AddVariantFlow.waiting_for_quantity)
            await message.answer(
                "Теперь напишите количество варианта."
            )
            return
        
        await message.answer(
            "Почему из сервиса вариянта и из метода .get_VariantPrice не вернулся цена."
        )
    except ClientError as e:
        logger.warning(f"{e.log_message}")
        await message.answer(
            f"{e.user_message}"
        )
    except ServerError:
        logger.exception("Ошибка в хэндлере receiving_var_price")
        await message.answer(
            "Ошибка сервера."
        )
        await state.clear()
        
@router.message(AddVariantFlow.waiting_for_quantity)
async def receiving_var_quantity(message : Message, 
                                 variant_service : VariantService, 
                                 state : FSMContext):

    if message.from_user is None:
        await message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return
    
    if not message.text:
        await message.answer(
            "Вы не отправили количество"
        )
        return
    
    
    try:
        admin_data = await state.get_data()
        if not admin_data:
            await message.answer(
                "Словарь состояинй пуст"
            )
            await state.clear()
            return

        admin_id = message.from_user.id
        quantity = message.text
        parent_id = admin_data.get("parent_id")
        var_name = admin_data.get("var_name")
        var_price = admin_data.get("var_price")
        
        new_variant = await variant_service.finish_creating_variant(quantity = quantity,
                                                                  parent_id = parent_id,
                                                                  var_name = var_name,
                                                                  var_price = var_price,
                                                                  admin_id = admin_id
                                                                  )
        
        if new_variant:
            await message.answer(
                f"Вариянт по имени {var_name} успешно создался"
            )
            
        else:
            await message.answer(
                f"Вариянта по имени {var_name} не создался"
            )
        
        await state.clear()

    
    except ClientError as e:
        logger.warning(f"{e.log_message}")
        await message.answer(
            f"{e.user_message}"
        )    
        
    except ServerError:
        logger.exception("Ошибка в хэндлере receiving_var_quantity")
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

    await state.set_state(ShowVariantFlow.waiting_for_parent_name)



@router.message(ShowVariantFlow.waiting_for_parent_name)
async def get_parent_name_to_show_variant(message : Message, variant_service : VariantService, state : FSMContext):
    if message.from_user is None:
        await message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return

    user_id = message.from_user.id
    try:
        product_data = await variant_service.get_product_name_for_variant(user_id = user_id, parent_name = message.text, mode = OperationMode.READ)

        product_kb = create_item_table_buttons(data = product_data, action = "/show_variant")

        await message.answer(
            "Теперь выберите продукт чей варианты вы хотите увидеть.",
            reply_markup = product_kb
        )

        await state.update_data(parent_name = message.text)
        await state.set_state(ShowVariantFlow.waiting_for_parent_id)
    except ClientError as e:
        logger.warning(f"{e.log_message}", exc_info = True)
        await message.answer(
            f"{e.user_message}"
        )
    except ServerError:
        logger.exception("Ошибка в хэндлере get_parent_name_to_show_variant.")
        await message.answer(
            "Ошибка сервера."
        )
        await state.clear()

@router.callback_query(ShowVariantFlow.waiting_for_parent_id,
                       ItemCallback.filter(F.action == "/show_variant")
                       )
async def get_parent_id_to_show_variant(callback : CallbackQuery, 
                                        variant_service : VariantService,
                                        state : FSMContext
                                        ):
    
    if callback.from_user is None:
            await callback.answer()
            await callback.message.answer("Ошибка сервера.")
            logger.error("callback.from_user пустой.")
            await state.clear()
            return 


    if callback.data is None or callback.message is None:
            await callback.answer("Что то пошло не так.", show_alert = False)
            await state.clear()
            return

    try:

        show_variant_data = await state.get_data()
        parent_name = show_variant_data.get("parent_name")
        user_id = callback.from_user.id
        variant_data = await variant_service.get_parent_id_for_get_variant(parent_name = parent_name,
                                                                           text = text,
                                                                           user_id = user_id
                                                                           )

        await callback.answer()
        variant_kb = create_item_table_buttons(data = variant_data, action = "/show_variant")
        await state.update_data(parent_id = int(text))
        await state.set_state(ShowVariantFlow.waiting_for_variant_id)

        await callback.message.answer(
            "Теперь выберите вариянт продукта чьи данные вы хотите увидеть.",
            reply_markup = variant_kb
        )
    except AbsenceError as e:
            await callback.answer()
            logger.warning(f"{e.log_message}", exc_info = True)
            await callback.message.answer(
                f"{e.user_message}"
            )
            await state.clear()

    except ClientError as e:
        await callback.answer()
        logger.warning(f"{e.log_message}", exc_info = True)
        await callback.message.answer(
            f"{e.user_message}"
        )
    except ServerError:
        await callback.answer()
        logger.exception("Ошибка в хэндлере get_parent_id_to_show_variant.")
        await callback.message.answer(
            "Ошибка сервера."
        )
        await state.clear()

@router.callback_query(
    ShowVariantFlow.waiting_for_variant_id,
    ItemCallback.filter(F.action == "/show_variant")
)
async def finish_showing_variant(callback : CallbackQuery, 
                                 callback_data : ItemCallback,
                                 variant_service : VariantService, 
                                 state : FSMContext):

    if callback.from_user is None:
                await callback.answer()
                await callback.message.answer("Ошибка сервера.")
                logger.error("callback.from_user пустой.")
                await state.clear()
                return 
    
    
    if callback.data is None or callback.message is None:
            await callback.answer("Что то пошло не так.", show_alert = False)
            await state.clear()
            return
    
    await callback.answer()
    try:
        show_variant_data = await state.get_data()
        parent_id = show_variant_data.get("parent_id")
        parent_name = show_variant_data.get("parent_name")
        user_id = callback.from_user.id
        variant_id = callback_data.item_id
        found_variant = await variant_service.get_variant_to_show(parent_id = parent_id,
                                                                  parent_name = parent_name,
                                                                  ,
                                                                  user_id = user_id)

        await callback.message.answer(
            f"Продукт: {parent_name}\nВариант: {found_variant.var_name}\nЦена варианта: {found_variant.var_price}\nКоличество варианта {found_variant.stock_quantity}"
        )

        await state.clear()
    except ServerError:
        logger.exception("Ошибка в хэндлере finish_showing_variant")
        await callback.message.answer(
            "Ошибка сервера."
        )
        await state.clear()

    
    