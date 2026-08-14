import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ErrorEvent, Message
from pydantic import ValidationError

from bot.errors.client_error import ClientError
from bot.errors.server_error import ServerError

router = Router()

logger = logging.getLogger(__name__)

@router.error()
async def error_handler(event : ErrorEvent, state : FSMContext):
    exception = event.exception
    update = event.update

    clear_state = False
    user_message = "Ошибка Сервера"
    if isinstance(exception, ClientError):
        user_message = exception.user_message
        logger.warning(exception.log_message)
        clear_state = exception.clear_state
    elif isinstance(exception, ValidationError):

        logger_messsage = '; '.join(f"{'->'.join(str(loc) for loc in error['loc'])} : {error['msg']}" for error in exception.errors())
        logger.exception(f"{logger_messsage}")
        clear_state = True
    elif isinstance(exception, ServerError):

        logger.exception(exception.log_message)
        clear_state = True
    else:
        logger.exception("Ошибка сервера!")
        clear_state = True
        
        


    if isinstance(update, Message):
        await update.answer(
            f"{user_message}"
        )
    elif isinstance(update, CallbackQuery):
        if update.message is None:
            logger.exception("Message оказался пуст внутри update в error_handler.")
            return
        await update.message.answer(
            f"{user_message}"
        )

    if clear_state:
        await state.clear()