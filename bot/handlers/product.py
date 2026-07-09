from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.add_product import AddProductFlow
from bot.repositories.product import ProductRepository
from bot.services.product_service import ProductService
from bot.services.user_service import UserService
from bot.models import UserRole
from bot.errors.common_errors import BotError
from bot.tools.exist import check_exist




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
async def create_parent(message : Message, product_service : ProductRepository, state : FSMContext):
    if not message.text:
        await message.answer("Вы отправили пустую строку. Напишите имя продукта!")
        return
    
    parent_name = message.text

    existing_products = await product_service.get_all_parent_names_ids(parent_name = parent_name)

    if not existing_products:
        await message.answer(
            "Продукта и продуктов которые похожи по буквам на то что вы написали нету."
        )
        return
    
    if check_exist(names = existing_products, name = parent_name) == "exist":
        await message.answer(
            "Такой продукт уже сущетсвует."
        )
        return
    
    new_product = await product_service.create_product(parent_name = parent_name)

    if new_product is None:
        await message.answer("Товар не смог создан.")
        return
    
    await message.answer(f"Товар {parent_name} создался")
    await state.clear()
    return 


    
    