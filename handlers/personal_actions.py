print ('Personal_actions.py')

from aiogram import types
from dispatcher import dp, bot
import config
import re
import requests
import yt_dlp

import pandas as pd

from bot import BotDB
from aiogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from word import spacy_tokenizer
from model import find_similar_artists, compile_model

import asyncio
import ast

import config


#______________Для YOUTUBE____________________________________
class FilenameCollectorPP(yt_dlp.postprocessor.common.PostProcessor):
    def __init__(self):
        super().__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information['filepath'])
        return [], information
#______________________________________________________________


#________________Start________________________________

@dp.message_handler(commands = "start")
async def start(message: types.Message):
    
    if(not BotDB.user_exists(message.from_user.id)):    # Если нет пользователя в базе
        BotDB.add_user(message.from_user.id) 
        print('Создадим пользователя')           # Добавляем пользователя
    print('Пользователь создан')
    # Выводим сообщение
    await message.reply(f'{message.from_user.first_name}, добро пожаловать в чат бот по подбору музыкальных произведений!') # Отправим сообщение с приветствием.
    await message.bot.send_message(message.from_user.id, 'Этот бот позволяет вам осуществлять поиск музыки. Просто отправьте полное(или часть) название музыкального произведения!')   # Выводим сообщение
#________________________________________


#__________________________HELP___________________________
@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    user_name = message.from_user.first_name
    await message.reply(f'{user_name}, этот бот позволяет вам осуществлять поиск музыки. Просто отправьте \
                        полное(или часть) название музыкального произведения! \n')#this bot allows you to search for music. Just send the name of the track')#, album or artist.') # Отправим сообщение с приветствием.
    await message.bot.send_message(message.from_user.id, 'Набрав команду "/set_favorit" вы сможете сохранить в избранном \
                                   последнее предложенное Вам произведение. \n')
    await message.bot.send_message(message.from_user.id, 'Набрав команду "/favorits" вы сможете получить список: \
                                   название произведения, исполнителя, ссылку на \n')
#___________________________________________________________


#_______________________HISTORY_____________________________
# вывод истории
@dp.message_handler(commands=['history'])
async def history_handler(message: types.Message):
    Avtors = BotDB.get_avtors(message.from_user.id)     # заберём из бд всех прослушанных авторов
    await message.bot.send_message(message.from_user.id, 'Этих авторов вам бот выдавал вам с сылками на произведения: \n')
    await message.bot.send_message(message.from_user.id, Avtors)

    Tracks = BotDB.get_tracks(message.from_user.id)     # заберём из бд всех прослушанных произведений
    await message.bot.send_message(message.from_user.id, 'Такие произведения вы запрашивали ранее: \n')
    await message.bot.send_message(message.from_user.id, Tracks)

#_________________________________________________________


#__________________________upgrade___________________________
@dp.message_handler(commands=['upgrade']) # Фиксируем в избранном
async def faw_handler(message: types.Message):
    
    print(message.from_user.id)
    print(config.ADMIN_ID)

    print(type(message.from_user.id))
    print(type(config.ADMIN_ID))

    if message.from_user.id == int(config.ADMIN_ID) :
        print('hello admin')
        await message.bot.send_message(message.from_user.id,'Здравствуйте, админ. Сейчас одновим модель!')
        if await upgrade_model() is not False:
            print('Модель оновлена.')
            await message.bot.send_message(message.from_user.id,'Модель успешно обновлена!')
        else :
            print('Модель не обновилась.')
            await message.bot.send_message(message.from_user.id,'Ошибка! Модель не обновилась!!!')
    else:
        print('you not admin')
        user_name = message.from_user.first_name
        await message.reply(f'Здравствуйте, {user_name}! К сожалению данная функция доступна только Админу чата.')
        

    '''
    if BotDB.add_favorite(user_id= message.from_user.id,favorit=1): # Получим последний запрос юзера
        await message.bot.send_message(message.from_user.id,'Результат Вашего последнего поиска сохранён в избранном!')
    else:
        await message.bot.send_message(message.from_user.id,'К сожалению зезультат Вашего последнего поиска \
                                       не мог быть сохранён в избранном! Возможно вы ещё ни чего не искали.')
    '''
# ________________________________________________________



#__________________________SET Favorit___________________________
@dp.message_handler(commands=['set_favorit']) # Фиксируем в избранном
async def faw_handler(message: types.Message):
    if BotDB.add_favorite(user_id= message.from_user.id,favorit=1): # Получим последний запрос юзера
        await message.bot.send_message(message.from_user.id,'Результат Вашего последнего поиска сохранён в избранном!')
    else:
        await message.bot.send_message(message.from_user.id,'К сожалению зезультат Вашего последнего поиска \
                                       не мог быть сохранён в избранном! Возможно вы ещё ни чего не искали.')
# ________________________________________________________


#__________________________GET FAVORITS_____________________
@dp.message_handler(commands=['favorits'])  # Получение избранного
async def favorits_handler(message: types.Message):
    get_favorits = BotDB.get_all_favorits(message.from_user.id) # получение всех записей избранного
    await message.bot.send_message(message.from_user.id,'Вот результат:')
    await message.bot.send_message(message.from_user.id, get_favorits)
#______________________________________________________________


#__________________________GET SIMILAR____________________
@dp.message_handler(commands=['similar'])  # Получение избранного
async def get_similar_handler(message: types.Message):
    last_artist = BotDB.get_last_artist(message.from_user.id) # Получим артиста из последнего запроса
    
    if last_artist is not False: # Если есть результат последнего поиска произведения
        print('Последний артист был - ', last_artist)    # Для наладки
        
        similar_artists = await find_similar_artists(last_artist)   # Получим рекомендованных артистов
    
        if similar_artists is not False:
            #print(similar_artists)
            await message.bot.send_message(message.from_user.id,'C этим артистом , \
                                           часто слушают следующих артистов: ')
            await message.bot.send_message(message.from_user.id, similar_artists)
        
        else:
            await message.bot.send_message(message.from_user.id,'К сожалению, я пока не могу вам рекомендовать \
                                           подходящих артистов, так как в нашей базе ВЫ ПЕРВЫЙ ))), кто решил \
                                           сделать такой поиск, для данного артиста. Я запомню ваш запрос, и \
                                           уже скоро, я смогу его использовать для рекоммендаций. Спасибо Вам!!! \
                                            ')


    else:   # Если не искали произведения
        await message.bot.send_message(message.from_user.id,'К сожалению, я не могу выдать вам подходящих артистов,\
                                        потому, что не нахожу результат вашего последнего поиска. \
                                        Пожалуйста, сделайте запрос на поиск произведения, и потом повторите запрос \
                                        на поиск других артистов. Спасибо.')
#______________________________________________________________

#__________________ПОИСК ССЫЛКИ НА YOUTUBE_______________________
async def youtube(tracks, number, message: types.Message):
    
    tmp = tracks[number]['artist'] + tracks[number]['name']
    
    YDL_OPTIONS = {'format': 'bestaudio/best',
                   'noplaylist': 'True',
                   'postprocessors': [{
                       'key': 'FFmpegExtractAudio',
                       'preferredcodec': 'mp3',
                       'preferredquality': '192'
                   }],
                   }
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            filename_collector = FilenameCollectorPP()
            ydl.add_post_processor(filename_collector)
            video = ydl.extract_info(f"ytsearch:{tmp}", download=False)
            await message.reply(video['entries'][0]['original_url'])
            #print(video['entries'][0]['original_url'])  ### ССЫЛКА НА ЮТУБ
        except:
            await message.reply('Не удалось найти трек на youtube')

    link_youtube = video['entries'][0]['original_url']  # запомним ссылку с ютуба
    return link_youtube
#_________________________________________________________________________________


#_________________ОБНОВЛЕНИЕ МОДЕЛИ_______________________
async def upgrade_model():

    new_data = BotDB.upgrade()  # Получим данные для обновления с базы данных
    df = pd.DataFrame(new_data, columns=['user_id', 'artist_name', 'scrobbles'])
        
    # Прочитайте существующие CSV файлы
    file1 = pd.read_csv("lastfm_artist_list.csv")
    file2 = pd.read_csv("lastfm_user_scrobbles.csv")
        
    # Создадим new_artist, отфильтруем df, оставив только строки с artist_name, которых нет в file1:
    # выбираются новые артисты (artist_name), которых еще нет в file1, используя операцию isin()
    new_artists = df[~df['artist_name'].isin(file1['artist_name'])]
   
    # создается новый столбец artist_id с помощью функции range(), начиная с длины file1 и заканчивая 
    # длиной file1 + длина новых артистов.
    new_artists['artist_id'] = range(len(file1), len(file1) + len(new_artists))
    
    # новые артисты со столбцами artist_id и artist_name добавляются в file1 с помощью функции pd.concat(), 
    # игнорируя индексы с помощью параметра ignore_index=True.
    file1 = pd.concat([file1, new_artists[['artist_id', 'artist_name']]], ignore_index=True)
    

    # Теперь создадим new_users, отфильтруем df, оставив только строки с user_id, которых нет в file2:
    # выбираются новые артисты (user_id), которых еще нет в file2, используя операцию isin()
    new_users = df[~df['user_id'].isin(file2['user_id'])]
    
    # Объединение DataFrame по столбцу artist_name
    new_users_combined = pd.merge(new_users, file1, on='artist_name')
    #print(new_users_combined)

    # новые пользователи со столбцами users_id, artist_id и scrobbles добавляются в file2 с помощью функции pd.concat(), 
    # игнорируя индексы с помощью параметра ignore_index=True.
    file2 = pd.concat([file2, new_users_combined[['user_id', 'artist_id', 'scrobbles']]], ignore_index=True)
    
    if file1.to_csv("lastfm_artist_list.csv", index=False) is not False :
    #if file1.to_csv("updated_lastfm_artist_list.csv", index=False) is not False :
        print("file1 upload")
    else:
        print('error file1 upload')

    if file2.to_csv("lastfm_user_scrobbles.csv", index=False) is not False :
    #if file2.to_csv("updated_lastfm_user_scrobbles.csv", index=False) is not False :
        print("file2 upload")
    else:
        print('error file2 upload')

    await compile_model()
    print('файлы и модель обновили')
    return


#________________________________________________________________

#____________________ВЫБОР ПОИСКА ПРОИЗВЕДЕНИЯ НА YouTube_________________
    
@dp.callback_query_handler(lambda c: c.data in ['1','2','3','4','5','6','7','8','9','10'])
async def process_callback_button(callback_query: types.CallbackQuery):
    number = int(callback_query.data)-1
    
    last_request = BotDB.load_response_user(user_id=callback_query.from_user.id)
    request = ast.literal_eval(last_request)
                                    
    link_youtube = await youtube(request, number, callback_query.message)
    
    MSG_text = BotDB.load_query_user(user_id = callback_query.from_user.id)



    #_______________________ПРОВЕРКА НА ТЕКУШЕГО АРТИСТА______________
    check = BotDB.check_artist(user_id=callback_query.from_user.id, artist=request[number]["artist"], 
                               track=request[number]["name"])
    '''
    if check is not None:
        print ('True = ', check)
    else:
        print ('False = ', check)
    '''
    #_________________________________________________________________

    #_________________СОХРАНИМ ЗАПРОС В БД____________________________
    
    BotDB.add_record1(callback_query.from_user.id,     # Сохраним запрос и результат в бд
                      query=MSG_text, 
                      track=request[number]["name"],
                      artist=request[number]["artist"],
                      favorit =0,
                      link=link_youtube,
                      check = check)
    #print(message.from_user.id)
    #________________________________________________________


    '''
    if callback_query.data == '1':
        # Код для обработки callback-запроса от кнопки 1
        await callback_query.answer('Вы нажали на кнопку 1')
    '''    
#_____________________________________________________________________



#_______________________HANDLER()_________________
@dp.message_handler()
async def rocess_message(message: types.Message):
    global tracks  # Объявляем переменную tracks как глобальную
    MSG_text = spacy_tokenizer(message.text)    # Удалим из запроса знаки припинания (импорт функции из word)

    #print(len(MSG_text))
    if MSG_text=='':
        await message.bot.send_message(message.from_user.id,
                                       'После обработки запроса получилось пустое значение запроса.')
        await message.bot.send_message(message.from_user.id, 
                                       'Введите, пожалуйста, запрос с буквами и больше 2 символов.')
                                                                     
        #print('После обработки запроса получилось пустое значение запроса.')
        #print('Введите, пожалуйста, запрос с буквами.')
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name
    await message.reply('Сейчас посмотрим, какие есть прозведения содежащие Вашу информацию: '+ MSG_text)


    BotDB.save_query_user( user_id = message.from_user.id, query_user = MSG_text)
    
    #_______________________ПОИСК ТРЕКА НА САЙТЕ__________________
    tracks = []
    print(MSG_text)
     # Устанавливаем параметры и отправляем запрос к MusicBrainz Api
    url2 = f"http://musicbrainz.org/ws/2/release/?query={MSG_text}&fmt=json"
    result2 = requests.get(url2).json()
    #print(result2)
    for release in result2['releases']:
        tracks.append({
            'name': release['title'],
            'artist': release['artist-credit'][0]['artist']['name']
        })
        #print(release)
    
    track=tracks[0]["name"]
    artist=tracks[0]["artist"]    
    #________________________________________________________________
    


    #________________________СОХРАНЕНИЕ ОТВЕТА НА ЗАПРОС_____________
    BotDB.save_response_user(user_id=message.from_user.id, last_request = str(tracks))
    #print('сохранили запрос')
    #_________________________________________________________________
    
    #___________НИЖНЯЯ КЛАВИАТУРА_________________________________
    '''
    # KeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('1')
    item2 = types.KeyboardButton('2')
    item3 = types.KeyboardButton('3')
    item4 = types.KeyboardButton('4')

    markup.add(item1, item2, item3, item4)
    await message.reply(text_output, reply_markup=markup)
    '''
    #_______________________________________________________________


    #___________________ПОДГОТОВКА КЛАВИАТУРЫ ДЛЯ СООБЩЕНИЯ_________
    # InlineKeyboard
    
    markup = types.InlineKeyboardMarkup(row_width=5)
    item1 = types.InlineKeyboardButton('№1', callback_data='1') 
    item2 = types.InlineKeyboardButton('№2', callback_data='2') 
    item3 = types.InlineKeyboardButton('№3', callback_data='3') 
    item4 = types.InlineKeyboardButton('№4', callback_data='4')
    item5 = types.InlineKeyboardButton('№5', callback_data='5')
    item6 = types.InlineKeyboardButton('№6', callback_data='6')
    item7 = types.InlineKeyboardButton('№7', callback_data='7')
    item8 = types.InlineKeyboardButton('№8', callback_data='8') 
    item9 = types.InlineKeyboardButton('№9', callback_data='9')
    item10 = types.InlineKeyboardButton('№10', callback_data='10')

    #markup.add(item1, item2, item3, item4, item5, item6, item7, item8, item9, item10)
    #________________________________________________________________


    #____________ВЫВОД ТРЕКА ПОЛЬЗОВАТЕЛЮ___________________________
    text_output = "Вот список произведений и авторов!!!\n"
    len_tracks = int(len(tracks))
    #print(tracks)
    #print(len_tracks)
    if  len_tracks !=0: 
        if len_tracks >= 14 :
            len_tr = 10
        else:
            len_tr = (len_tracks)

        for i in range(int(len_tr)):
            text_output += f'{i+1}. Музыкальное произведение : {tracks[i]["name"]}, автор : {tracks[i]["artist"]}.\n '

        button_list = [types.InlineKeyboardButton(f'№{i+1}', callback_data=str(i+1)) for i in range(len_tr)]
        markup.add(*button_list)

        await message.reply(text_output, reply_markup=markup)
        
    else :
        text_output = "К сожалению по вашему запросу я не смог найти это произведение. Давайте поробуем другой запрос.\n"
        await message.reply(text_output)
    #______________________________________________________________

    new_data = BotDB.upgrade()  # Получим данные для обновления
    df = pd.DataFrame(new_data, columns=['user_id', 'artist_name', 'scrobbles'])
        
    # Прочитайте существующие CSV файлы
    file1 = pd.read_csv("lastfm_artist_list.csv")
    file2 = pd.read_csv("lastfm_user_scrobbles.csv")
        
    # Создадим new_artist, отфильтруем df, оставив только строки с artist_name, которых нет в file1:
    # выбираются новые артисты (artist_name), которых еще нет в file1, используя операцию isin()
    new_artists = df[~df['artist_name'].isin(file1['artist_name'])]
   
    # создается новый столбец artist_id с помощью функции range(), начиная с длины file1 и заканчивая 
    # длиной file1 + длина новых артистов.
    new_artists['artist_id'] = range(len(file1), len(file1) + len(new_artists))
    
    # новые артисты со столбцами artist_id и artist_name добавляются в file1 с помощью функции pd.concat(), 
    # игнорируя индексы с помощью параметра ignore_index=True.
    file1 = pd.concat([file1, new_artists[['artist_id', 'artist_name']]], ignore_index=True)
    

    # Теперь создадим new_users, отфильтруем df, оставив только строки с user_id, которых нет в file2:
    # выбираются новые артисты (user_id), которых еще нет в file2, используя операцию isin()
    new_users = df[~df['user_id'].isin(file2['user_id'])]
    
    # Объединение DataFrame по столбцу artist_name
    new_users_combined = pd.merge(new_users, file1, on='artist_name')
    #print(new_users_combined)

    # новые пользователи со столбцами users_id, artist_id и scrobbles добавляются в file2 с помощью функции pd.concat(), 
    # игнорируя индексы с помощью параметра ignore_index=True.
    file2 = pd.concat([file2, new_users_combined[['user_id', 'artist_id', 'scrobbles']]], ignore_index=True)
    
    if file1.to_csv("lastfm_artist_list.csv", index=False) is not False :
        print("file1 upload")
    else:
        print('error file1 upload')

    if file2.to_csv("lastfm_user_scrobbles.csv", index=False) is not False :
        print("file2 upload")
    else:
        print('error file2 upload')


    #__________Предложение продолжить поиск______________________
    #await message.reply(text_output)
    await message.bot.send_message(message.from_user.id,'Нажмите нужный номер трека, что бы получить на него ссылку, или можем поискать что-нибудь ещё...)) ')
    #__________________________________________________________

   
#_________________________________________________________________________________

