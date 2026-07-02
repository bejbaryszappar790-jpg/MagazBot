from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from bot.crud.user import search_user, register_user
from bot.schemas.sessionstart import SessionStart_In
router = Router()


@router.message(CommandStart())
async def start_session(message : Message, session : AsyncSession):

    if message.from_user is None:
        await message.answer("Неизвестный пользователь!")
        return
    
    
    user_id = message.from_user.id


    input = SessionStart_In(user_id = user_id)

    existing_user = await search_user(session = session, user_id = input.user_id)

    if existing_user:
        await message.answer("Добро пожаловать снова!")
        return

    
    new_user = await register_user(session = session, user_id = input.user_id)
    
    if new_user is None:
        await message.answer("Пользователь не был создан в базе данных!")
        return
    
    await message.answer("Добро Пожаловать!")
    return

