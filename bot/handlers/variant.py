from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.states.add_variant import AddVariantFlow
from bot.models import UserRole
from bot.crud.product import (
    get_all_parent_names_ids, 
    create_variant
    )
from bot.tools.chekc_userRole import check_user_role
from bot.keyboard.products import create_product_buttons




router = Router()


@router.message(Command("add_variant"))
async def check_parent_name(message : Message, session : AsyncSession, state : FSMContext):
    if message.from_user is None:
        await message.answer(
            "Id пользователя не найден"
        )
        return
    

    admin_id = message.from_user.id

    admin_role = check_user_role(session = session, user_id = admin_id)

    if admin_role is None:
        await message.answer(
            "Пользователь не зарегестрирован!"
        )
        return
    
    if admin_role != UserRole.ADMIN:
        await message.answer(
            "Пользователь должен быть админом!"
        )
        return
    
    await state.set_state(AddVariantFlow.waiting_for_parent_name)

    await message.answer(
        "Отправьте имя продукта к которому хотите добавить вариянт."
    )


@router.message(AddVariantFlow.waiting_for_parent_name)
async def receiving_parent_name(message : Message, session : AsyncSession, state : FSMContext):
    if message.text is None or message.text == "":
        await message.answer(
            "Вы ничего не написали!"
        )
        return
    
    parent_name = message.text
    existing_products = await get_all_parent_names_ids(session = session, parent_name = parent_name)
    attributes = existing_products["attributes"]
    if parent_name not in attributes:
        await message.answer(
            "Такого продукта не существует!!!"
        )
        return
    
    builder = create_product_buttons(data = attributes)
    
    await message.answer(
        "Выберите продукт которому хотите добавить вариянт.",
        reply_markup = builder
    )

@router.callback_query(
    AddVariantFlow.waiting_for_parent_id,
    F.data.startswith("product_")
    )
async def receiving_parent_id(callback : CallbackQuery, session : AsyncSession, state : FSMContext):
    if callback.data is None:
        callback.message.answer("Что то пошло не так.")
        return
    
    parent_id = callback.data.split("_")[1]

    if parent_id is None:
        await callback.message.answer(
            ""
        )
    
    
        