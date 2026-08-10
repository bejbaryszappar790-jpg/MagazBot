import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pydantic import ValidationError

from bot.errors.client_error import ClientError
from bot.errors.server_error import ServerError


logger = logging.getLogger(__name__)
Так = начал писать helper теперь надо сделать так что бы helper знал когда ошибка ValidationError был вызван пользователе а когда сервером
и надо вызвать эту функцию.
async def handle_error(event : Message | CallbackQuery, 
                              error : Exception, 
                              state : FSMContext | None = None,
                              log_message : str | None = None,
                              user_message: str | None = None,

                              ):


    if isinstance(error, ClientError):
        logger.warning(f"{error.log_message}")
        user_answer = error.user_message
    elif isinstance(error, ServerError):
        logger.exception(f"{error}")
        user_answer = "Ошибка сервера."
    elif isinstance(error, ValidationError):
        logger.exception()

                    
    if isinstance(event, Message):
        await event.answer(
            f"{user_answer}"
        )
    elif isinstance(event, CallbackQuery):
        
        if event.message is None:
            logger.error("Нету аттрибута message внутри экземпляра класса CallbackQuery")
            await event.answer("Что то пошло не так", show_alert = True)
            return
        await event.answer()
        await event.message.answer(f"{user_answer}")
    else:
        logger.error("пришло другой тип событий которого мы не рассмотрели")
    if state:
        await state.clear()

    