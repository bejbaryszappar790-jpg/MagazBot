import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pydantic import ValidationError

from bot.callback_factories.item_callback import ItemCallback
from bot.enums import OperationMode
from bot.errors.client_error import AbsenceError, ClientError
from bot.errors.server_error import ServerError
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
        input_data = VerifyUser(user_id = message.from_user.id)
        result = await user_service.verify_user(admin_id = input_data.user_id
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
    except ValidationError:
        logger.error(f"Pydantic не смог валидировать id пользоваеля {message.from_user.id}")
        await message.answer(
            "Ошибка сервера."
        )
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
        input_data = GetProductNameForVariant(user_id = message.from_user.id, parent_name = message.text, mode = OperationMode.WRITE)
        product_data = await variant_service.get_product_name_for_variant(parent_name = input_data.parent_name, 
                                                                       user_id = input_data.user_id,
                                                                       mode = input_data.mode
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
    except ValidationError:
        logger.warning(f"Имя продукты который был отправен пользователем {message.from_user.id} вызвал ошибку валидаций у pydantic в хэндлере receiving_parent_name", exc_info = True)
        await message.answer(
            "Вы не правильно написали parent_name!\nНапишите имя продукта и она не должно быть пустым или же нажмите на кнопку отмена!"
        )
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
                              callback_data : ItemCallback,
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
    try:
        input_data = GetProductIdForVariant(parent_id = callback_data.item_id, admin_id = callback.from_user.id)
        result = await variant_service.get_product_id_for_variant(parent_id = input_data.parent_id,
                                                            admin_id = input_data.admin_id
                                                            )

        if not result:
            logger.error("Метод get_product_id_for_variant не вернул True в хэндлере receiving_parent_id.")
            await callback.message.answer(
                "Ошибка сервера."
            )
            return
        
        await state.update_data(parent_id = input_data.parent_id)
        await state.set_state(AddVariantFlow.waiting_for_variant_name)

        await callback.message.answer(
            "Напишите имя варианта которую вы хотите добавить."
        )
    except ValidationError:
        logger.warning(f"Pydantic не смог валидировать id товара {callback_data.item_id} который был выбран пользователем {callback.from_user.id}", exc_info = True)
        await callback.message.answer(
            "Ошибка сервера!"
        )
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

    if not admin_data:
        logger.error("Словарь FSM пуст в хэндлере receiving_var_name")
        await message.answer(
            "Ошибка сервера."
        )
        return
    
    
    try:
        input_data = GetVariantName(**admin_data)
        result = await variant_service.get_variant_name(variant_name = input_data.variant_name, 
                                                 parent_id = input_data.parent_id,
                                                 admin_id = input_data.admin_id
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
    except ValidationError:
            logger.exception(f"Pydantic не смог валидировать имя товара {message.text} который был выбран пользователем {message.from_user.id}")
            await message.answer(
                "Ошибка сервера!"
            )
    except ClientError as e:
        logger.warning(f"{e.log_message}", exc_info = True)
        await message.answer(
            f"{e.user_message}"
        )
    except ServerError:
        logger.warning("Ошибка в хэндлере receiving_var_name")
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

    try:
        data_dict = {
            "input_price" : message.text,
            "admin_id" : message.from_user.id    
        }
        input_data = GetVariantPrice(**data_dict)

        variant_price = variant_service.get_variant_price(
            input_price = input_data.input_price,
            admin_id = input_data.admin_id
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
    except ValidationError:
        logger.warning(f"Pydantic не смог валидировать цену {message.text}")
        await message.answer(
            "Неправильно ввели цену!"
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
        
        data_dict = {
            "quantity" : message.text,
            **admin_data
        }

        input_data = ReceivingVarQuantity(**data_dict)
        
        new_variant = await variant_service.finish_creating_variant(quantity = input_data.quantity,
                                                                  parent_id = input_data.parent_id,
                                                                  var_name = input_data.var_name,
                                                                  var_price = input_data.var_price,
                                                                  admin_id = input_data.admin_id
                                                                  )
        
        if new_variant:
            logger.info(f"Пользователь {input_data.admin_id} создал вариант {input_data.var_name} продукта с id {input_data.parent_id}")
            await message.answer(
                f"Вариянт по имени {input_data.var_name} успешно создался"
            )
            
        else:
            logger.error(f"Пользователь {input_data.admin_id} не смог создать вариант {input_data.var_name} продукта {input_data.parent_id}")
            await message.answer(
                "Ошибка сервера."
            )
        
        await state.clear()

    except ValidationError:
        logger.warning(f"Pydantc вызвал ошибку при вводе цене варианта которого пытался создалть пользователь {message.from_user.id}.")
        await message.answer(
            "Вы не правильно ввели цену.\nПримеры записи цены: 100, 100,0, 100.0"
        )
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

    data_dict = {
        "user_id" : message.from_user.id,
        "parent_name" : message.text,
        "mode" : OperationMode.READ
    }

    
    try:
        input_data = GetProductNameForVariant(**data_dict)
        product_data = await variant_service.get_product_name_for_variant(user_id = input_data.user_id, parent_name = input_data.parent_name, mode = input_data.mode)

        product_kb = create_item_table_buttons(data = product_data, action = "/show_variant")

        await message.answer(
            "Теперь выберите продукт чей варианты вы хотите увидеть.",
            reply_markup = product_kb
        )

        await state.update_data(parent_name = message.text)
        await state.set_state(ShowVariantFlow.waiting_for_parent_id)
    except ValidationError:
        logger.warning(f"Пользователь {data_dict.get("user_id")} не написал имя продукта.")
        await message.answer(
            "Вы не написали имя продукта!"
        )
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
                                        callback_data : ItemCallback,
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
    

    show_variant_data = await state.get_data()
    data_dict = {
        "parent_id" : callback_data.item_id,
        "user_id" : callback.from_user.id,
        **show_variant_data
    }
    try:
        input_data = GetParentIdForGetVariant(**data_dict)
        variant_data = await variant_service.get_parent_id_for_get_variant(parent_name = input_data.parent_name,
                                                                           parent_id = input_data.parent_id,
                                                                           user_id = input_data.user_id
                                                                           )

        await callback.answer()
        variant_kb = create_item_table_buttons(data = variant_data, action = "/show_variant")
        await state.update_data(parent_id = input_data.parent_id)
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
    except ValidationError:
        logger.error(f"Pydantic не смог валидировать id продукта от пользователя {data_dict.get("user_id")}")
        await callback.message.answer(
            "Ошибка сервера."
        )
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
    show_variant_data = await state.get_data()
    data_dict = {
        **show_variant_data,
        "variant_id" : callback_data.item_id,
        "user_id" : callback.from_user.id
    }
    try:
        input_data = GetVariantToShow(**data_dict)
    
        found_variant = await variant_service.get_variant_to_show(parent_id = input_data.parent_id,
                                                                  parent_name = input_data.parent_name,
                                                                  variant_id = input_data.variant_id,
                                                                  user_id = input_data.user_id
                                                                  )
        await callback.message.answer(
            f"Продукт: {input_data.parent_name}\nВариант: {found_variant.var_name}\nЦена варианта: {found_variant.var_price}\nКоличество варианта {found_variant.stock_quantity}"
        )

        await state.clear()
    except ValidationError:
        logger.error(f"Pydantic не смог получить вариант {data_dict.get("parent_name")} продукта {data_dict.get("parent_id")}")
        await callback.message.answer(
            "Ошибка сервера."
        )
    except ServerError:
        logger.exception("Ошибка в хэндлере finish_showing_variant")
        await callback.message.answer(
            "Ошибка сервера."
        )
        await state.clear()

    
    