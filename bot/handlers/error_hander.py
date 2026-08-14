import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import ErrorEvent
from pydantic import ValidationError

from bot.errors.client_error import ClientError
from bot.errors.server_error import ServerError

router = Router()

logger = logging.getLogger(__name__)

@router.error()
async def error_handler(event : ErrorEvent, state : FSMContext):
    if state is None:
        logger.error("FSMContext нету внутри error_handler")
        return
    
    exception = event.exception
    update = event.update

    clear_state = False
    user_message = "Ошибка Сервера"
    if isinstance(exception, ClientError):
        user_message = exception.user_message
        logger.warning(exception.log_message)
        clear_state = exception.clear_state
    elif isinstance(exception, ValidationError):

        logger_message = '; '.join(f"{'->'.join(str(loc) for loc in error['loc'])} : {error['msg']}" for error in exception.errors())
        logger.error(f"{logger_message}", exc_info = True) #noqa: LOG014
        clear_state = True
    elif isinstance(exception, ServerError):

        logger.error(exception.log_message, exc_info = True) #noqa: LOG014
        clear_state = True
    else:
        logger.error("Ошибка сервера!", exc_info = True) #noqa: LOG014
        clear_state = True
        
    if update.message is not None:
        message = update.message
        await message.answer(
            f"{user_message}"
        )
    elif update.callback_query is not None:
        callback = update.callback_query

        if callback.message is None:
            await callback.answer(
                "Ошибка сервера ",
                show_alert = True
            )
            if state is not None:
                await state.clear()
            return

        await callback.answer()
        await callback.message.answer(
            f"{user_message}"
        )

    if clear_state and state is not None:
        await state.clear()