print('in bot.db')

from aiogram import executor

from dispatcher import dp, bot_startup
import handlers

from db import BotDB
BotDB = BotDB('accountant.db')  # Присоеденим файл базы данных.


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=bot_startup)    