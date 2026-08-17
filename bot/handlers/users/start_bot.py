import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.enums import UserType
from bot.services.user_services import UserService

router = Router()

logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def start_session(message : Message, user_service : UserService):

    if message.from_user is None:
        await message.answer("Неизвестный пользователь!")
        return
    

    user_type = await user_service.process_user_start(admin_id = message.from_user.id)

    if user_type is UserType.EXISTING:
        await message.answer(
            "Добро Пожаловать снова!"
        )  
    elif user_type == UserType.NEW:
        await message.answer(
            "Добро Пожаловать."
        )
            
  
    

