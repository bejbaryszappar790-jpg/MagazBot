from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from bot.states.add_variant import AddVariantFlow
from bot.services.variant_services import VariantService
from bot.services.user_services import UserService
from bot.services.product_services import ProductService
from bot.errors.common_errors import (
    BotError,
    AbsenseError,
    SimpleValidationError,
    NoneError,

    )
from bot.keyboard.products import create_product_buttons
from bot.tools.exist import check_exist





router = Router()


@router.message(Command("add_variant"))
async def check_parent_name(message : Message,  
                            variant_service : VariantService, 
                            user_service : UserService,
                            state : FSMContext
                            ):
    if message.from_user is None:
        await message.answer(
            "Id пользователя не найден"
        )
        await state.clear()
        return
    

    try:
        result = await variant_service.start_creating_variant(admin_id = message.from_user.id, 
                                                              user_repo = user_service.user_repo
                                                              )
        if result:
            await state.set_state(AddVariantFlow.waiting_for_parent_name)

            await message.answer(
                "Отправьте имя продукта к которому хотите добавить вариант."
            )
            return
        
        await message.answer(
            "Почему то в хэндлере с командой /add_variant сервис не вернула True."
        )
        await state.clear()
    except BotError as e:
        await message.answer(
            f"Ошибка: {e}"
        )
   
    


@router.message(AddVariantFlow.waiting_for_parent_name)
async def receiving_parent_name(message : Message, 
                                variant_service : VariantService,
                                product_service: ProductService, 
                                state : FSMContext
                                ):
    if not message.text:
        await message.answer(
            "Вы ничего не написали!"
        )
        return
    
    try:
        product_data = await variant_service.get_ProductNameForVariant(parent_name = message.text, 
                                                       product_repo = product_service.product_repo
                                                       )
        
        if product_data:
            kb = create_product_buttons(data = product_data)
            await state.set_state(AddVariantFlow.waiting_for_parent_id)

            await message.answer(
                "Выберите продукт которому хотите добавить вариант.",
                reply_markup = kb
            )
            return
        await message.answer(
            "Почему то product_data пуст."
        )
        await state.clear()
    except BotError as e:
        await message.answer(
            f"Ошибка: {e}"
        )


@router.callback_query(
    AddVariantFlow.waiting_for_parent_id,
    F.data.startswith("product_")
    )
async def receiving_parent_id(callback : CallbackQuery, 
                              variant_service : VariantService, 
                              product_service : ProductService,
                              state : FSMContext
                              ):
    
    if callback.data is None or callback.message is None:
        await callback.answer("Что то пошло не так.", show_alert = False)
        await state.clear()
        return
    
    await callback.answer()
    
    try:
        parent_id = variant_service.get_ProductIdForVariant(callback_data = callback.data,
                                                            product_repo = product_service.product_repo
                                                            )
        
        if parent_id:
            await state.update_data(parent_id = parent_id)
            await state.set_state(AddVariantFlow.waiting_for_variant_name)

            await callback.message.answer(
                "Напишите имя варианта которую вы хотите добавить."
            )
            return
        
        await callback.message.answer(
            "Почему то parent_id пуст"
        )
        await state.clear()
    except AbsenseError as e:
        await callback.message.answer(
            f"Ошибка: {e}"
        )
        
        await state.clear()
    except SimpleValidationError as e:
        await callback.message.answer(
            f"Ошибка: {e}"
        )



@router.message(AddVariantFlow.waiting_for_variant_name)
async def receiving_var_name(message : Message, variant_service : VariantService, state : FSMContext):
    if not message.text: 
        await message.answer(
            "Напишите имя варианта!"
        )
        return
    

    admin_data = await state.get_data()

    parent_id = admin_data.get("parent_id", None)
    if parent_id is None:
        await message.answer(
            "Мы не смогли получить id продукта."
        )
        await state.clear()
        return
    
    try:
        result = variant_service.get_VariantName(variant_name = message.text, 
                                                 parent_id = parent_id
                                                 )
        if result:
            
            await state.update_data(var_name = message.text)

            await state.set_state(AddVariantFlow.waiting_for_price)
            await message.answer(
                "Теперь напишите цену варианта."
            )
            return
        await message.answer(
            "Ошибка: Почему то result получисля False"
        )
    except BotError as e:
        await message.answer(
            f"{e}"
        )

@router.message(AddVariantFlow.waiting_for_price)
async def receiving_var_price(message : Message, 
                              variant_service : VariantService,
                              state : FSMContext):
    if message.text is None:
        await message.answer(
            "Вы не написали цену!"
        )
        return
    
    try:
        variant_price = variant_service.get_VariantPrice(input_price = message.text)
        
        if variant_price:
            await state.update_data(variant_price = variant_price)
            await state.set_state(AddVariantFlow.waiting_for_quantity)
            await message.answer(
                "Теперь напишите количество варианта."
            )
            return
        
        await message.answer(
            "Почему из сервиса вариянта и из метода .get_VariantPrice не вернулся цена."
        )
    except BotError as e:
        await message.answer(
            f"{e}"
        )
        
@router.message(AddVariantFlow.waiting_for_quantity)
async def receiving_var_quantity(message : Message, 
                                 variant_service : VariantService, 
                                 product_service : ProductService,
                                 state : FSMContext):
    if not message.text:
        await message.answer(
            "Вы не отправили количество"
        )
        return
    
    
    try:
        admin_data = await state.get_data()
        if not admin_data:
            await message.answer(
                "Словарь состояинй пуст"
            )
            return
        
        
    
    except NoneError as e:
        await message.answer(
            f"{e}"
        )
        await state.clear()
        return
    except AbsenseError as e:
        await message.answer(
            f"{e}"
        )
        await state.clear()
        
    except BotError as e:
        await message.answer(
            f"{e}"
        )
        return
    
"""
TO DO: 
finish handler and check it,
also learn to work with real interpretator in python and read mistakes which interpretator displays.
also test all layer for my commands in tg.
"""