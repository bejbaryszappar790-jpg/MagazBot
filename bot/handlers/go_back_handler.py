import logging

from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_factories.command_callback import CommandCallback
from bot.enums import RegressButtonText, RegressButtonType
from bot.errors.server_error import ServerError
from bot.keyboard.reply_cancel_go_back_kb import reply_cancel_go_back_kb
from bot.services.variant_services import VariantService
from bot.utils.back_navigarion_map import GLOBAL_BACK_NAVIGATION
from bot.utils.make_go_back_cancel_shorter import make_go_back_cancel_shorter

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(
        or_f(
            CommandCallback.filter(F.type == RegressButtonType.GO_BACK),
            CommandCallback.filter(F.type == RegressButtonType.CANCEL)
        )
        )
async def callback_go_back_cancel_handler(
    callback : CallbackQuery, 
    variant_service :  VariantService,
    callback_data : CommandCallback,
    state : FSMContext
):
    if callback.message is None:
        logger.error("callback.message пуст внутри callback_go_back_cancel_handler")
        await callback.answer("Ошибка сервера", show_alert = True)
        return


    await callback.answer()
    current_state = await state.get_state()
    navigation_back_dict = GLOBAL_BACK_NAVIGATION.get(current_state)
    
    if callback_data.type == RegressButtonType.CANCEL:
        await callback.message.answer(
            """
            Вы отменили всю команду.
            Выберите команду.
            """
        )
        logger.info(f"Пользователь {callback.from_user.id} отменил команду в состояний {current_state} и вышел полностью из команды {callback_data.action} с {callback_data.type}")
        await state.clear()
        return
    
    if navigation_back_dict is None:
        await callback.message.answer(
            """
            Так как вы были на шаге 1, нажав назад вы отменили команду!
            Выберите команду!
            """
        )
        logger.info(f"Пользователь {callback.from_user.id} нажал на кнопку назад в первом шаге в команде {callback_data.action}")
        await state.clear()
        return


    previous_state = navigation_back_dict["previous"]
    message_for_user = navigation_back_dict["text"]
    table = navigation_back_dict.get("kb")


    await state.set_state(previous_state)

    if table is None:
        kb = reply_cancel_go_back_kb()
        await callback.message.answer(message_for_user, reply_markup = kb)
    else:
        state_data = await state.get_data()
        kb = await make_go_back_cancel_shorter(variant_service = variant_service, state_data = state_data, table = table)
        await callback.message.answer(
            message_for_user,
            reply_markup = kb
        )
        

@router.message(
    or_f(F.text == RegressButtonText.GO_BACK, F.text == RegressButtonText.CANCEL)
)
async def message_go_back_cancel_handler(message : Message, variant_service : VariantService, state : FSMContext):

    if message.from_user is None:
        raise ServerError("Id пользоваетля не опознан")
    
    current_state = await state.get_state()
    navigation_back_dict = GLOBAL_BACK_NAVIGATION.get(current_state)
    state_data = await state.get_data()
    if message.text == RegressButtonText.CANCEL:
        await message.answer(
            """
            Вы отменили всю команду.
            Выберите команду.
            """
        )
        logger.info(f"Пользователь {message.from_user.id} отменил команду в состояний {current_state} и вышел полностью из команды {state_data.get("action")}")
        await state.clear()
        return
    
    if navigation_back_dict is None:
        await message.answer(
            """
            Так как вы были на шаге 1, нажав назад вы отменили команду!
            Выберите команду!
            """
        )
        logger.info(f"Пользователь {message.from_user.id} нажал на кнопку назад в первом шаге в команде {state_data.get("action")}")
        await state.clear()
        return


    previous_state = navigation_back_dict["previous"]
    message_for_user = navigation_back_dict["text"]
    table = navigation_back_dict.get("kb")


    await state.set_state(previous_state)

    if table is None:
        await message.answer(message_for_user)
    else:
        kb = await make_go_back_cancel_shorter(variant_service = variant_service, state_data = state_data, table = table)
        await message.answer(
            message_for_user,
            reply_markup = kb
        )
    