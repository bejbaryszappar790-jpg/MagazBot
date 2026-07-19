from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.add_product import AddProductFlow
from bot.services.product_services import ProductService
from bot.services.user_services import UserService
from bot.errors.common_errors import BotError




router = Router()


@router.message(Command("add_product"))
async def ask_name(message : Message, 
                   product_service : ProductService,
                   user_service : UserService,
                    state : FSMContext):


    if message.from_user is None:
        await message.answer("Бот не нашел id пользователя")
        return
    
   
    try:
    
        result = await product_service.start_asking_name(admin_id = message.from_user.id, 
                                                        user_repo = user_service.user_repo)
        
        if result:
            await state.set_state(AddProductFlow.waiting_for_name)
            await message.reply("Введите имя товара:")
            return
    except BotError as e:
        await message.answer(
            f"Ошибка: {e}"
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
    except BotError as e:
        await message.answer(
            f"Ошибка: {e}"
        )

