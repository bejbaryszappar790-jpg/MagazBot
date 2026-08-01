import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.states.add_variant import AddVariantFlow
from bot.services.variant_services import VariantService
from bot.services.user_services import UserService
from bot.services.product_services import ProductService
from bot.errors.server_error import (
    ServerError
    )
from bot.errors.client_error import (
    ClientError,
)
from bot.keyboard.products import create_product_buttons



logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("add_variant"))
async def check_parent_name(message : Message,  
                            variant_service : VariantService, 
                            state : FSMContext
                            ):
    if message.from_user is None:
        await message.answer(
            "Id пользователя не найден"
        )
        await state.clear()
        return
    

    try:
        result = await variant_service.start_creating_variant(admin_id = message.from_user.id
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
    


@router.message(AddVariantFlow.waiting_for_parent_name)
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
                                                                       admin_id = admin_id
                                                       )
        
        if product_data:
            kb = create_product_buttons(data = product_data)
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
    F.data.startswith("product_")
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
        text = callback.data.split("_")[1]
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
    
