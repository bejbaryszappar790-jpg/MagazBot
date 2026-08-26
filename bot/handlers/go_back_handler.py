import logging

from aiogram import F, Router
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.callback_factories.command_callback import CommandCallback
from bot.enums import RegressButtonType
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
    
    if callback.data == RegressButtonType.CANCEL:
        await callback.message.answer(
            """
            Вы отменили всю команду.
            Выберите команду.
            """
        )
        logger.info(f"Пользователь {callback.from_user.id} отменил команду в состояний {current_state} и вышел полностью из команды {callback_data.action}")
        await state.clear()
        return
    
    if navigation_back_dict is None:
        await callback.message.answer(
            """
            Так как вы были на шаге 1, нажав назад вы отменили команду!
            Выберите команду!
            """
        )
        logger.info(f"Пользователь {callback.from_user} нажал на кнопку назад в первом шаге в команде {callback_data.action}")
        await state.clear()
        return


    previous_state = navigation_back_dict["previous"]
    message_for_user = navigation_back_dict["text"]
    table = navigation_back_dict.get("kb")


    await state.set_state(previous_state)

    if table is None:
        await callback.message.answer(message_for_user)
    else:
        state_data = await state.get_data()
        kb = await make_go_back_cancel_shorter(variant_service = variant_service, state_data = state_data, table = table)
        await callback.message.answer(
            message_for_user,
            reply_markup = kb
        )
        
        
    