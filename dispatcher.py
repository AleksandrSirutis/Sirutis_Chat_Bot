print('in dispatcher.py')

import logging
from aiogram import Bot, Dispatcher

import config

from aiogram import types
from aiogram.types import BotCommand


# Сконфигурируем логи
logging.basicConfig(level=logging.INFO)

# Проверка
if not config.BOT_TOKEN:        # Проверка на наличие токена
    exit("No token provided")

# init
bot = Bot(token=config.BOT_TOKEN)#, parse_mode="HTML")    # Создадим экземпляр класса bot и передадим а него наш токен.
dp = Dispatcher(bot)    # Создадим экземпляр класса Dispatcher и передадим в него класс бот.


#_____________ПРИ ЗАПУСКЕ БОТА_____________________

async def bot_startup(dispatcher: dp):     #Код при старте
    #print('создим меню')
    await dispatcher.bot.set_my_commands([     # Создадим меню команд
        BotCommand("help", "Помощь"),
        BotCommand("history", "История"),
        BotCommand("start", "Cтарт"),
        BotCommand("favorits", "Избранное"),
        BotCommand("set_favorit", "Добавить в избранное"),
        BotCommand("similar", "подобрать похожих артистов"),
        BotCommand("upgrade", "обновить модель, доступно только админу.")
    ])
#_________________________________________________

