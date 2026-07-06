from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.states.add_product import AddProductFlow

from bot.models import UserRole
from bot.crud.product import (
    create_product, 
    get_all_parent_names_ids, 
    )
from bot.tools.check_userRole import check_user_role
from bot.tools.exist import check_exist




router = Router()


@router.message(Command("add_product"))
async def ask_name(message : Message, 
                   session : AsyncSession,
                    state : FSMContext):


    if message.from_user is None:
        await message.answer("Бот не нашел id пользователя")
        return
    
   
    admin_id = message.from_user.id

    admin_role = await check_user_role(session = session, user_id = admin_id)

    if admin_role is None:
        await message.answer(
            "Пользователь не зарегестрирован!"
        )
        return
    
    if admin_role != UserRole.ADMIN:
        await message.answer(
            "Пользователь должен быть админом!"
        )
        return
    
    
    
    await state.set_state(AddProductFlow.waiting_for_name)
    await message.reply("Введите имя товара:")





@router.message(AddProductFlow.waiting_for_name)
async def create_parent(message : Message, session : AsyncSession, state : FSMContext):
    if not message.text:
        await message.answer("Вы отправили пустую строку. Напишите имя продукта!")
        return
    
    parent_name = message.text

    existing_products = await get_all_parent_names_ids(session = session, parent_name = parent_name)

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
    
    new_product = await create_product(session = session, parent_name = parent_name)

    if new_product is None:
        await message.answer("Товар не смог создан.")
        return
    
    await message.answer(f"Товар {parent_name} создался")
    await state.clear()
    return 


    
    