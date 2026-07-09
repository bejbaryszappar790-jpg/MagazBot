from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.services.user_service import UserService
from bot.errors.common_errors import BotError

router = Router()


@router.message(CommandStart())
async def start_session(message : Message, user_service : UserService):

    if message.from_user is None:
        await message.answer("Неизвестный пользователь!")
        return
    
    try:
        answer = await user_service.process_user_start(admin_id = message.from_user.id)

        if answer:
            await message.answer(
                "Добро Пожаловать снова!"
            )  
        else:
            await message.answer(
                "Добро Пожаловать."
            )
            
    except BotError as e:
        await message.answer(
            f"Ошибка: {e}"
        )

    

