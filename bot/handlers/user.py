import logging
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.services.user_services import UserService
from bot.errors.server_error import ServerError
from bot.enums import UserType

router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start_session(message : Message, user_service : UserService):

    if message.from_user is None:
        await message.answer("Неизвестный пользователь!")
        return
    
    try:
        user_type = await user_service.process_user_start(admin_id = message.from_user.id)

        if user_type is UserType.EXISTING:
            await message.answer(
                "Добро Пожаловать снова!"
            )  
        elif user_type == UserType.NEW:
            await message.answer(
                "Добро Пожаловать."
            )
            
    except ServerError:
        logger.exception("Ошибка в хэндлере start_session")
        await message.answer(
            "Ошибка сервера."
        )

    

