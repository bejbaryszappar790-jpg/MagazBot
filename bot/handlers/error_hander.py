import logging

from aiogram import Router
from aiogram.types import ErrorEvent, Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.errors.client_error import ClientError


router = Router()

logger = logging.getLogger(__name__)

@router.error()
async def error_handler(event : ErrorEvent, state : FSMContext):
    exception = event.exception
    update = event.update

    clear_state = False
    if isinstance(exception, ClientError):
        user_message = exception.user_message
        logger.warning(f"{exception.log_message}")
    else:
        user_message = "Ошибка сервера!"
        logger.exception(f"{exception.args[0]}")
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

    if exception.clear_state or clear_state:
        await state.clear()

    Надо дорабобать случаи с ValidationError который был вызван со стороны сервера и кроме этого очистить хэндлеры от try/except и запустить и протестить бота!


    
    
