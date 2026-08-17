import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.enums import ThingType
from bot.schemas.products.creatingproduct import CreatingProduct
from bot.schemas.users.verifyuser import VerifyUser
from bot.services.product_services import ProductService
from bot.services.user_services import UserService
from bot.states.add_product import AddProductFlow
from bot.tools.helper import validate_user_input

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("add_product"))
async def ask_name(message : Message, 
                   user_service : UserService,
                    state : FSMContext):


    if message.from_user is None:
        await message.answer("Бот не нашел id пользователя")
        return
    
   
    
    service_args = VerifyUser(user_id = message.from_user.id)
    result = await user_service.verify_user(admin_id = service_args.user_id,
                                            thing_type = ThingType.PRODUCT
                                            )
    
    if result:
        await state.set_state(AddProductFlow.waiting_for_name)
        await state.update_data(admin_id = message.from_user.id)
        await message.reply("Введите имя товара:")
        return
    





@router.message(AddProductFlow.waiting_for_name)
async def create_parent(message : Message, product_service : ProductService, state : FSMContext):
    if message.from_user is None:
        await message.answer("Ошибка сервера.")
        logger.error("message.from_user пустой.")
        await state.clear()
        return
    
    if not message.text:
        await message.answer("Вы отправили пустую строку. Напишите имя продукта!")
        return

    state_data = await state.get_data()

    data = {
        "admin_id" : state_data.get("admin_id"),
        "parent_name" : message.text
    }

    service_args = validate_user_input(schema = CreatingProduct, data = data, user_id = message.from_user.id, validated_data = "parent_name")
    new_product = await product_service.creating_product(parent_name = service_args.parent_name, admin_id = service_args.admin_id)
    
    await message.answer(
        f"Продукт по имени {message.text} создался!"
    )
    logger.info(f"Пользователь {service_args.admin_id} успешно создал товар {new_product.parent_name} с id {new_product.parent_id}")
    await state.clear()
