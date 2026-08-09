import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from pydantic import ValidationError

from bot.enums import ThingType
from bot.errors.client_error import ClientError
from bot.errors.server_error import (
    ServerError,
)
from bot.schemas.products.creatingproduct import CreatingProduct
from bot.schemas.users.verifyuser import VerifyUser
from bot.services.product_services import ProductService
from bot.services.user_services import UserService
from bot.states.add_product import AddProductFlow

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("add_product"))
async def ask_name(message : Message, 
                   user_service : UserService,
                    state : FSMContext):


    if message.from_user is None:
        await message.answer("Бот не нашел id пользователя")
        return
    
   
    try:
        input_data = VerifyUser(user_id = message.from_user.id)
        result = await user_service.verify_user(admin_id = input_data.user_id,
                                                thing_type = ThingType.PRODUCT
                                                )
        
        if result:
            await state.set_state(AddProductFlow.waiting_for_name)
            await message.reply("Введите имя товара:")
            return
    except ValidationError:
        logger.error(f"Pydantic не смог валидировать id пользователь {message.from_user.id}")
        await message.answer(
            "Ошибка сервера."
        )
    except ClientError as e:
        logger.warning(f"{e.log_message}", exc_info = True)
        await message.answer(
            f"{e.user_message}"
        )
    except ServerError:
        logger.exception("Ошибка в хэндлере для старта создание продукта.")
        await message.answer(
            "Ошибка сервера."
        )
        await state.clear()





@router.message(AddProductFlow.waiting_for_name)
async def create_parent(message : Message, product_service : ProductService, state : FSMContext):
    if message.from_user is None:
        await message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return
    
    if not message.text:
        await message.answer("Вы отправили пустую строку. Напишите имя продукта!")
        return


    try:
        input_data = CreatingProduct(admin_id = message.from_user.id, parent_name = message.text)
        result = await product_service.creating_product(parent_name = input_data.parent_name, admin_id = input_data.admin_id)
        if result:
            await message.answer(
                f"Продукт по имени {message.text} создался!"
            )
            await state.clear()
    except ValidationError:
        logger.warning(f"Пользователь {message.from_user.id} не написал имя.")
        await message.answer(
            "Вы не написали имя!"
        )
    except ClientError as e:
        logger.warning(f"{e.log_message}", exc_info = True)
        await message.answer(
            f"Ошибка: {e.user_message}"
        )
        
    except ServerError:
        logger.exception("Ошибка в хэндлере create_parent.")
        await message.answer(
            "Ошибка со стороны сервера."
        )

