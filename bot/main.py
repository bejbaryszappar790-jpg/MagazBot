import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message
from aiogram.filters import Command
from dotenv import load_dotenv


load_dotenv()
bot_token = os.getenv("BOT_TOKEN", "")



async def set_main_menu(bot : Bot):
    
    main_menu_commands = [
        BotCommand(command = "Добавить_Продукт", description = "Добавляет новый продукт"),
        BotCommand(command = "Добаввить_Вариянт", description = "Добавляет новый вариянт"),
        BotCommand(command = "Показать_Цену_Вариянта", description = "Показывает цену вариянта"),
        BotCommand(command = "Изменить_Цену_Варията", description = "Меняет цену вариянта."),
        BotCommand(command = "Увидеть_Кол_Вариянта", description = "Показывает количество вариянта"),
        BotCommand(command = "Изменить_Кол_Вариянта", description = "Меняет количество вариянта"),
    ]

    await bot.set_my_commands(main_menu_commands)


async def cmd_status(message : Message):
    message.answer("Статус бота: Хороший")

async def main():
    bot = Bot(token = bot_token)
    
    
    dp = Dispatcher()

    dp.message.register(cmd_status, Command("status"))

    dp.startup.register(set_main_menu)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
