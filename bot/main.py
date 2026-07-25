import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message
from aiogram.filters import Command
from dotenv import load_dotenv
from bot.middleware.db import DbSessionMiddleware
from bot.handlers.user import router as user_router
from bot.handlers.variant import router as variant_router
from bot.handlers.product import router as product_router
from bot.database import SessionLocal

load_dotenv()

bot_token = os.getenv("BOT_TOKEN", "")

if not os.path.exists("logs"):
    os.makedirs("logs")

general_handler = logging.FileHandler("logs/bot.log", mode = "a", encoding = "utf-8")
error_handler = logging.FileHandler("logs/errors.log", mode = "a", encoding = "utf-8")
error_handler.setLevel(logging.ERROR)


logging.basicConfig(
    level = logging.INFO,
    format = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s",
    handlers = [
        general_handler,
        error_handler
    ]
)

logger = logging.getLogger(__name__)

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


async def main():
    bot = Bot(token = bot_token)
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool = SessionLocal))


    dp.include_router(user_router)
    dp.include_router(variant_router)
    dp.include_router(product_router)

    dp.startup.register(set_main_menu)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot was interrupted by keyboard with Ctrl + C!")
