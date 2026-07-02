from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.states.add_product import AddProductFlow
from bot.crud.user import search_user
from bot.models import UserRole
from bot.crud.product import create_product

router = Router()


@router.message(Command("add_product"))
async def ask_name(message : Message, 
                   session : AsyncSession,
                    state : FSMContext):


    if message.from_user is None:
        await message.answer("Бот не нашел id пользователя")
        return
    
    admin_id = message.from_user.id
    
    admin = await search_user(session = session, user_id = admin_id)
    
    if admin is None:
        await message.answer("Не удалось найти пользователя")
        return
    
    if admin.user_role != UserRole.ADMIN:
        await message.answer("Пользователь должен быть админом что бы добить товар!")
        return
    
    
    await state.set_state(AddProductFlow.waiting_for_name)
    await message.reply("Введите имя товара:")

@router.message(AddProductFlow.waiting_for_name)
async def create_parent(message : Message, session : AsyncSession, state : FSMContext):
    if message.text is None or message.text == "":
        await message.answer("Вы отправили пустую строку. Напишите имя продукта!")
        return
    
    parent_name = message.text
    new_product = await create_product(session = session, parent_name = parent_name)

    if new_product is None:
        await message.answer("Товар не смог создан.")
        return

    await state.clear()
    await message.answer(f"Товар {parent_name} создался")
    return 