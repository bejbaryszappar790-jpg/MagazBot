import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

from bot.database import SessionLocal
from bot.handlers.error_hander import router as error_router
from bot.handlers.go_back_handler import router as go_back_cancel_handler
from bot.handlers.products.add_product import router as add_product_router
from bot.handlers.users.start_bot import router as start_bot_router
from bot.handlers.variants.add_variant import router as add_variant_router
from bot.handlers.variants.show_variant import router as show_variant_router
from bot.handlers.variants.update_variant import router as update_variant_router
from bot.middleware.db import DbSessionMiddleware

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
        BotCommand(command = "show_variant", description = "Показывает цену и количество варианта"),
        BotCommand(command = "update_variant", description = "Обновляет либо имя либо цену либо количество варианта")
    ]

    await bot.set_my_commands(main_menu_commands)


async def main():
    bot = Bot(token = bot_token)
    dp = Dispatcher()
    try:
        dp.update.middleware(DbSessionMiddleware(session_pool = SessionLocal))


        dp.include_router(go_back_cancel_handler)
        dp.include_router(error_router)
        dp.include_router(start_bot_router)
        dp.include_router(add_variant_router)
        dp.include_router(show_variant_router)
        dp.include_router(add_product_router)
        dp.include_router(update_variant_router)

        dp.startup.register(set_main_menu)

    
        await dp.start_polling(bot)
    except Exception:
        logger.exception("Ошибка в main.py")
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot was interrupted by keyboard with Ctrl + C!")
