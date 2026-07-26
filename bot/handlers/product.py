import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.add_product import AddProductFlow
from bot.services.product_services import ProductService
from bot.errors.server_error import (
    ServerError,
    )
from bot.errors.client_error import (
    ClientError
)


logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("add_product"))
async def ask_name(message : Message, 
                   product_service : ProductService,
                    state : FSMContext):


    if message.from_user is None:
        await message.answer("Бот не нашел id пользователя")
        return
    
   
    try:
    
        result = await product_service.start_asking_name(admin_id = message.from_user.id)
        
        if result:
            await state.set_state(AddProductFlow.waiting_for_name)
            await message.reply("Введите имя товара:")
            return
    except ClientError as e:
        logger.warning(f"{e}")
        await message.answer(
            f"{e}"
        )
    except ServerError as e:
        logger.exception(f"{e}")
        await message.answer(
            "Ошибка со стороны сервера."
        )





@router.message(AddProductFlow.waiting_for_name)
async def create_parent(message : Message, product_service : ProductService, state : FSMContext):
    if not message.text:
        await message.answer("Вы отправили пустую строку. Напишите имя продукта!")
        return
    

    try:
        result = await product_service.creating_product(parent_name = message.text)
        if result:
            await message.answer(
                f"Продукт по имени {message.text} создался!"
            )
            await state.clear()
    except ClientError as e:
        logger.warning(f"{e}", exc_info = True)
        await message.answer(
            f"Ошибка: {e}"
        )
        
    except ServerError as e:
        logger.exception(f"{e}")
        await message.answer(
            "Ошибка со стороны сервера."
        )

