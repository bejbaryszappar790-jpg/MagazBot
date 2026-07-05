import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message
from aiogram.filters import Command
from dotenv import load_dotenv
from bot.middleware.db import DbSessionMiddleware
from bot.handlers.product import router as supplier_router
from bot.handlers.user import router as user_router
from bot.handlers.variant import router as variant_router
from bot.handlers.product import router as product_router
from bot.database import SessionLocal

load_dotenv()

bot_token = os.getenv("BOT_TOKEN", "")



async def set_main_menu(bot : Bot):
    
    main_menu_commands = [
        BotCommand(command = "add_product", description = "Добавляет новый продукт"),
        BotCommand(command = "add_variant", description = "Добавляет новый вариант"),
        BotCommand(command = "show_var_price", description = "Показывает цену варианта"),
        BotCommand(command = "change_var_price", description = "Меняет цену варианта."),
        BotCommand(command = "show_var_quantity", description = "Показывает количество варианта"),
        BotCommand(command = "change_var_quantity", description = "Меняет количество варианта"),
    ]

    await bot.set_my_commands(main_menu_commands)


async def cmd_status(message : Message):
    await message.answer("Статус бота: Хороший")

async def main():
    bot = Bot(token = bot_token)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool = SessionLocal))

    dp.include_router(supplier_router)
    dp.include_router(user_router)
    dp.include_router(variant_router)
    dp.include_router(product_router)

    dp.message.register(cmd_status, Command("status"))

    dp.startup.register(set_main_menu)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
