from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.repositories.user import UserRepository
from bot.schemas.sessionstart import SessionStart_In
router = Router()


@router.message(CommandStart())
async def start_session(message : Message, user_repo : UserRepository):

    if message.from_user is None:
        await message.answer("Неизвестный пользователь!")
        return
    
    
    user_id = message.from_user.id


    input = SessionStart_In(user_id = user_id)

    existing_user = await user_repo.search_user(user_id = input.user_id)

    if existing_user:
        await message.answer("Добро пожаловать снова!")
        return

    
    new_user = await user_repo.register_user(user_id = input.user_id)
    
    if new_user is None:
        await message.answer("Пользователь не был создан в базе данных!")
        return
    
    await message.answer("Добро Пожаловать!")
    return

