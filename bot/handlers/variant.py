from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from bot.states.add_variant import AddVariantFlow
from bot.models import UserRole
from bot.crud.product import (
    get_all_parent_names_ids,
    search_product_byid
    )
from bot.crud.variant import (
    create_variant
)
from bot.tools.check_userRole import check_user_role
from bot.keyboard.products import create_product_buttons




router = Router()


@router.message(Command("add_variant"))
async def check_parent_name(message : Message, session : AsyncSession, state : FSMContext):
    if message.from_user is None:
        await message.answer(
            "Id пользователя не найден"
        )
        await state.clear()
        return
    

    admin_id = message.from_user.id

    admin_role = await check_user_role(session = session, user_id = admin_id)

    if admin_role is None:
        await message.answer(
            "Пользователь не зарегестрирован!"
        )
        await state.clear()
        return
    
    if admin_role != UserRole.ADMIN:
        await message.answer(
            "Пользователь должен быть админом!"
        )
        await state.clear()
        return
    
    await state.set_state(AddVariantFlow.waiting_for_parent_name)

    await message.answer(
        "Отправьте имя продукта к которому хотите добавить вариант."
    )


@router.message(AddVariantFlow.waiting_for_parent_name)
async def receiving_parent_name(message : Message, session : AsyncSession, state : FSMContext):
    if not message.text:
        await message.answer(
            "Вы ничего не написали!"
        )
        return
    
    parent_name = message.text
    existing_products = await get_all_parent_names_ids(session = session, parent_name = parent_name)
    attributes = existing_products["attributes"]
    is_exist = False
    for key in attributes.keys():
        if key.lower() == parent_name.lower():
            is_exist = True
            break

    if not is_exist:
        await message.answer(
            "Такого продукта не существует!"
        )  
        return
    builder = create_product_buttons(data = attributes)
    await state.set_state(AddVariantFlow.waiting_for_parent_id)

    await message.answer(
        "Выберите продукт которому хотите добавить вариант.",
        reply_markup = builder
    )

@router.callback_query(
    AddVariantFlow.waiting_for_parent_id,
    F.data.startswith("product_")
    )
async def receiving_parent_id(callback : CallbackQuery,  state : FSMContext):
    if callback.data is None or callback.message is None:
        await callback.answer("Что то пошло не так.", show_alert = False)
        await state.clear()
        return
    
    await callback.answer()

    text = callback.data.split("_")[1]

    try:
        parent_id = int(callback.data.split("_")[1])
        

        
        
        await state.update_data(parent_id = parent_id)
        await state.set_state(AddVariantFlow.waiting_for_variant_name)

        await callback.message.answer(
            "Напишите имя варианта которую вы хотите добавить."
        )
        return
    except ValueError:
        await callback.message.answer(
            f"Почему то мы не нашли продукт по id {text} в базе данных."
        )
        await state.clear()

@router.message(AddVariantFlow.waiting_for_variant_name)
async def receiving_var_name(message : Message, state : FSMContext):
    if not message.text: 
        await message.answer(
            "Напишите имя варианта!"
        )
        return
    
    await state.update_data(var_name = message.text)

    await state.set_state(AddVariantFlow.waiting_for_price)
    await message.answer(
        "Теперь напишите цену варианта."
    )
    

@router.message(AddVariantFlow.waiting_for_price)
async def receiving_var_price(message : Message, state : FSMContext):
    if message.text is None:
        await message.answer(
            "Вы не написали цену!"
        )
        return
    
    try:
        price_text = message.text.replace(",", ".")
        price = float(price_text)
        if price < 0.0:
            await message.answer(
                "Надо написать число равно или больше нуля!"
            )
            return
        
        await state.update_data(price = price)
        await state.set_state(AddVariantFlow.waiting_for_quantity)
        await message.answer(
            "Теперь напишите количество варианта."
        )
    except ValueError:
        await message.answer(
            "Напишите дробно число например как 100 или 10.50!"
        )
        
@router.message(AddVariantFlow.waiting_for_quantity)
async def receiving_var_quantity(message : Message, session : AsyncSession, state : FSMContext):
    if not message.text:
        await message.answer(
            "Вы не отправили количество"
        )
        return
    
    
    try:
        quantity = int(message.text)
        if quantity < 0:
            await message.answer(
                "Надо написать число равно или больше нуля!"
            )
            return
        
        admin_data = await state.get_data()

        parent_id = admin_data.get("parent_id", None)

        if parent_id is None:
            await message.answer(
                "Мы не смогли найти товар, проблема с БД"
            )
            await state.clear()
            return
        
        var_name = admin_data.get("var_name", "")
        
        if not var_name:
            await message.answer(
                "Название варианта не нашли, что-то ту не в порядке."
            )
            await state.clear()
            return
        
        var_price = admin_data.get("price", 0.0)
        if var_price is None:
            await message.answer(
                "Не правильная цена!"
            )
            await state.clear()
            return
        
        parent_obj = await search_product_byid(session = session, parent_id = parent_id)

        if parent_obj is None:
            await message.answer(
                "Не смогли найти продукт в базе данных!"
            )
            await state.clear()
            return
        
        new_variant = await create_variant(session = session, 
                                     parent_product = parent_obj,
                                     var_name = var_name,
                                     var_price = var_price,
                                     quantity = quantity
                                     )
        
        if new_variant is None:
            await message.answer(
                "Что то пошло не так вариант не создался"
            )
            await state.clear()
            return
        
        await state.clear()
        await message.answer(
            f"Продукт {var_name} с ценой: {var_price} и с количеством {quantity} создался"
        )
        return
    except ValueError:
        await message.answer(
            "Отправьте целое число которое будет отображать количество варианта котрого вы хотите добавить."
        )
        return
