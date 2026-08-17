import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.callback_factories.item_callback import ItemCallback
from bot.enums import OperationMode
from bot.keyboard.item_table import create_item_table_buttons
from bot.schemas.products.getparentidforgetvariant import GetParentIdForGetVariant
from bot.schemas.products.getproductnameforvariant import GetProductNameForVariant
from bot.schemas.variants.getvarianttoshow import GetVariantToShow
from bot.services.variant_services import VariantService
from bot.states.show_variant import ShowVariantFlow
from bot.tools.helper import validate_user_input

logger = logging.getLogger(__name__)

router = Router()




@router.message(Command("show_variant"))
async def start_showing_variant(message : Message, state : FSMContext):
    if message.from_user is None:
        logger.warning("Неизвестный пользователь без телеграм id пытался увидеть вариант.")
        await message.answer(
            "Вы не зарегестрированы."
        )
        await state.clear()
        return

    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} успешно начал команду /show_variant.")
    await message.answer(
        "Теперь напишите имя продукта чьей вариант хотите увидеть!"
    )
    await state.update_data(user_id = message.from_user.id)
    await state.set_state(ShowVariantFlow.waiting_for_parent_name)



@router.message(ShowVariantFlow.waiting_for_parent_name)
async def get_parent_name_to_show_variant(message : Message, variant_service : VariantService, state : FSMContext):

    state_data = await state.get_data()

    data = {
            "parent_name" : message.text,
            "mode" : OperationMode.READ,
            **state_data
        }
    service_args = validate_user_input(schema = GetProductNameForVariant, data = data, user_id = state_data.get("user_id"), validated_data = "parent_name")
    product_data = await variant_service.get_product_name_for_variant(id = service_args.user_id, parent_name = service_args.parent_name, mode = service_args.mode)

    product_kb = create_item_table_buttons(data = product_data, action = "/show_variant")

    await message.answer(
        "Теперь выберите продукт чей варианты вы хотите увидеть.",
        reply_markup = product_kb
    )

    await state.update_data(parent_name = message.text)
    await state.set_state(ShowVariantFlow.waiting_for_parent_id)


@router.callback_query(ShowVariantFlow.waiting_for_parent_id,
                       ItemCallback.filter(F.action == "/show_variant")
                       )
async def get_parent_id_to_show_variant(callback : CallbackQuery, 
                                        variant_service : VariantService,
                                        callback_data : ItemCallback,
                                        state : FSMContext
                                        ):
    if callback.data is None or callback.message is None:
            await callback.answer("Что то пошло не так.", show_alert = False)
            await state.clear()
            return
    
    
    state_data = await state.get_data()
    

    data = {
            "parent_id" : callback_data.item_id,
            **state_data
    }
    service_args = GetParentIdForGetVariant(**data)
    variant_data = await variant_service.get_parent_id_for_get_variant(parent_name = service_args.parent_name,
                                                                        parent_id = service_args.parent_id,
                                                                        user_id = service_args.user_id
                                                                        )

    await callback.answer()
    variant_kb = create_item_table_buttons(data = variant_data, action = "/show_variant")
    await state.update_data(parent_id = service_args.parent_id)
    await state.set_state(ShowVariantFlow.waiting_for_variant_id)
    
    await callback.message.answer(
        "Теперь выберите вариянт продукта чьи данные вы хотите увидеть.",
        reply_markup = variant_kb
    )
    

@router.callback_query(
    ShowVariantFlow.waiting_for_variant_id,
    ItemCallback.filter(F.action == "/show_variant")
)
async def finish_showing_variant(callback : CallbackQuery, 
                                 callback_data : ItemCallback,
                                 variant_service : VariantService, 
                                 state : FSMContext):

    
    if callback.data is None or callback.message is None:
            await callback.answer("Что то пошло не так.", show_alert = False)
            await state.clear()
            return
    
    await callback.answer()
    state_data = await state.get_data()
    

    data = {
            **state_data,
            "variant_id" : callback_data.item_id
        }
    service_args = GetVariantToShow(**data)

    found_variant = await variant_service.get_variant_to_show(parent_id = service_args.parent_id,
                                                                parent_name = service_args.parent_name,
                                                                variant_id = service_args.variant_id,
                                                                user_id = service_args.user_id
                                                                )
    await callback.message.answer(
        f"Продукт: {service_args.parent_name}\nВариант: {found_variant.var_name}\nЦена варианта: {found_variant.var_price}\nКоличество варианта {found_variant.var_quantity}"
    )

    await state.clear()
    