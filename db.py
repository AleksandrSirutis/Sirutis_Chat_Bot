print('in db.py')

import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()


    #________________*ПРОВЕРКА НА НАЛИЧИЯ ЮЗЕРА В БАЗЕ________
    def user_exists(self, user_id): # Проверяем, есть ли юзер в базе

        # Получим id из таблицы users где user_id равен текущему юзеру.
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))
    #________________________________________________________


    #________________СОХРАНИЕНИЕ ОВЕТА НА ЗАПРОС ЮЗЕРА________
    def save_response_user(self, user_id, last_request, ): #Сохраним последние рекомендации для пользователя
        
        # Добавим запись в таблицу users значение 
        self.cursor.execute("UPDATE `users` SET response_last_request = ? WHERE user_id = ?", (last_request, user_id))
        
        return self.conn.commit()
    #_________________________________________________________


    #________________СОХРАНИЕНИЕ ЗАПРОС ЮЗЕРА________
    def save_query_user(self, user_id, query_user, ): #Сохраним последние рекомендации для пользователя
        
        # Добавим запись в таблицу users значение 
        self.cursor.execute("UPDATE `users` SET query_user = ? WHERE user_id = ?", (query_user, user_id))
        self.conn.commit()
        return True
    #_________________________________________________________


    #________________ЗАГРУЗКА ОВЕТА НА ЗАПРОС ЮЗЕРА________
    def load_response_user(self, user_id): #Загрузим последние рекомендации для пользователя
        
        # Добавим запись в таблицу users значение user_id для нового пользователя
        last_request = self.cursor.execute("SELECT `response_last_request` FROM `users` WHERE `user_id` = ?", (user_id,))
        #print('загрузили запрос')
        self.conn.commit()
        return last_request.fetchone()[0]
    #_________________________________________________________


    #________________ЗАГРУЗКА ЗАПРОСА ЮЗЕРА________
    def load_query_user(self, user_id): #Загрузим последние рекомендации для пользователя
        
        # Добавим запись в таблицу users значение user_id для нового пользователя
        query_user = self.cursor.execute("SELECT `query_user` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()[0]
        #print('загрузили запрос')
        self.conn.commit()
        return query_user
    #_________________________________________________________



    #________________ПОЛУЧЕНИЕ ID ЮЗЕРА В ТАБЛИЦЕ ЮЗЕРОВ_______
    def get_user_id(self, user_id): #Достаем id юзера в базе по его user_id

        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()[0]
        return result
    #___________________________________________________________


    #________________*ДОБАВЛЕНИЕ НОВОГО ЮЗЕРА___________________

    def add_user(self, user_id):    #Добавляем юзера в базу

        # Добавим запись в таблицу users значение user_id для нового пользователя
        self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))
        if self.cursor.lastrowid:   # Проверим на наличие ошибок, вызванных выполнением запроса
               # .lastrowid если вставили новую строку с автоинкременом номера строки, то вернётся (ID) этой новой записи 
                return self.conn.commit()
        else:
                print('не смогли сохранить нового пользователя')
                return False
        
        #return self.conn.commit()
    #___________________________________________________________
      

    #_________________ПРОВЕРКА АРТИСТА И ПРОИЗВЕДЕНИЯ_________________
    def check_artist(self, user_id, artist, track):
        result = self.cursor.execute("SELECT `id` FROM `QUERY` WHERE user_id = ? AND artist = ? AND track = ?", 
                                    (user_id, artist, track,)).fetchone()
        check = None
        if result is not None:
            check = result[0]

        return check

    #_________________*СОХРАНЯЕМ В ИСТОРИЮ ЗАПРОС И РЕЗУЛЬТАТ____________
    def add_record1(self, user_id, query, track, artist, favorit, link, check):    # Сохраняем запрос

        if check is not None:   # Если такая запись уже существует, то добавим просмотр
            #print ('old')
            id=check
            #Добавляем запись о юзере, его запросе, рекоммендованном треке, является ли избранным и ссылку в ютуб.
            self.cursor.execute("UPDATE QUERY SET user_id=?, query=?, track=?, artist=?, favorit=?, link=?, scrobbles = scrobbles + 1 WHERE id = ?",
                (user_id,
                query, 
                track, 
                artist, 
                favorit,
                link,
                id))
            
            return self.conn.commit()
        
        
        else:   # Если такой записи нет, то создадим новую запись с одним просмотром
            #print ('New')
            #Создаем запись о юзере, его запросе, рекоммендованном треке, является ли избранным и ссылку в ютуб.
            self.cursor.execute("INSERT INTO QUERY (user_id, query, track, artist, favorit, link, scrobbles) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id,
                query, 
                track, 
                artist, 
                favorit,
                link,
                1))
            
            if self.cursor.lastrowid:   # Проверим на наличие ошибок, вызванных выполнением запроса
               # .lastrowid если вставили новую строку с автоинкременом номера строки, то вернётся (ID) этой новой записи 
                return self.conn.commit()
            else:
                return False

    #____________________________________________________________________


    #________________*ПОЛУЧЕНИЕ ПРОСЛУШАННЫХ АРТИСТОВ_____________________

    def get_avtors(self, user_id):  # Получить всех прослушанных артистов для текущего юзера.
        # Получим уникальных артистов для текущего юзера и отсортированных по артистам.
        self.cursor.execute("SELECT DISTINCT artist FROM QUERY WHERE user_id = ? ORDER BY artist", ((user_id),))

        OUT=[]
        out = self.cursor.fetchall()
     
        #out = []
        #row = self.cursor.fetchone()
        #while row is not None:
        #    out.append(row)
        #    row = self.cursor.fetchone()
            
        self.conn.commit() 
        return out
    #______________________________________________________________________


    #_________________ПОЛУЧИТЬ ВСЕ ПРОСЛУШАННЫЕ ПРОИЗВЕДЕНИЯ АРТИСТА___________

    def get_tracks_from_artist(self, user_id, artist):      # получить прослушанные произведения данного артиста
        # Получим уникальные произведения из таблицы QUERY, для текущего юзера и заданного артиста
        self.cursor.execute("SELECT DISTINCT track FROM QUERY WHERE user_id = ? AND artist = ? ORDER BY track", 
                            (user_id, artist))
        OUT=[]
        out = self.cursor.fetchall()
        self.conn.commit() 
        return out
    #______________________________________________________________________


    #_________________*ПОЛУЧИТЬ ВСЕ ПРОИЗВЕДЕНИЯ____________________________

    def get_tracks(self, user_id):      # получить все произведения по юзеру

        # Получить уникальные произведения из таблицы QUERY для текущего юзера, 
        # отсортированные по алфавиту по произведениям.
        self.cursor.execute("SELECT DISTINCT track FROM QUERY WHERE user_id = ? ORDER BY track", ((user_id),))
        OUT=[]
        out = self.cursor.fetchall()
        self.conn.commit() 
        return out
    #___________________________________________________________________


    #_________________ПОЛУЧЕНИЕ ВСЕЙ ПОСЛЕДНЕЙ СТРОКИ___________________

    def get_all(self, user_id):      # получить последнюю строку для юзера

        # Получить из таблицы QUERY где useer_id = текущий пользователь, 
        # значениевсей строки самого большого номера (последней записи)
        self.cursor.execute("SELECT * FROM QUERY ORDER BY user_id = ? DESC LIMIT 1 ", ((user_id),))
        OUT=[]
        out = self.cursor.fetchall()
        self.conn.commit() 
        return out
    #___________________________________________________________________


    #________________*ЗАФИКСИРОВАТЬ В ИЗБРАННОМ__________________________

    def add_favorite(self, user_id, favorit):   # Создаем запись в избранном
        
        # Получим id номер последней строки в таблице QUERY для текущего юзера
        last_id = self.cursor.execute("SELECT MAX(id) FROM QUERY WHERE user_id = ?", (user_id,)).fetchone()[0]
        #print(last_id)

        if last_id is not None: 
            # Запишем в таблицу QUERY в favorit метку активации с полученным id
            self.cursor.execute("UPDATE QUERY SET favorit = ? WHERE id = ?", (favorit, last_id))
            self.conn.commit()
            return True
        else:
            # обработка случая, когда нет строк, удовлетворяющих запросу
            self.conn.commit()
            return False
    #__________________________________________________________________


    #_________________*ПОЛУЧИТЬ ИЗБРАННОЕ_______________________________

    def get_all_favorits(self, user_id):      # получить избранное по артисту

        # Получим уникальные значения "произведения, артиста, ссылки из таблицы QUERY, 
        # для текущего юзера с отметкой что произведение избранное и отсортировать по артистам в алфавитном порядке(п/у)"
        self.cursor.execute("SELECT  DISTINCT track, artist, link FROM QUERY WHERE user_id = ? AND favorit=1 ORDER BY artist", ((user_id),))
        OUT=[]
        out = self.cursor.fetchall()
        self.conn.commit() 
        return out
    #_________________________________________________________________



    #________________*Подобрать похожего автора__________________________

    def get_last_artist(self, user_id):   # Создаем запись в избранном
        
        # Получим id номер последней строки в таблице QUERY для текущего юзера
        last_id = self.cursor.execute("SELECT MAX(id) FROM QUERY WHERE user_id = ?", (user_id,)).fetchone()[0]
        #print(last_id)
        #last_id = None  # Это для наладки

        if last_id is not None: 
            # Какой последний был артист
            artist = self.cursor.execute("SELECT artist FROM QUERY WHERE id = ?", (last_id,)).fetchone()[0]
            #print(artist)
            self.conn.commit()
            return artist
        else:
            # обработка случая, когда нет строк, удовлетворяющих запросу
            self.conn.commit()
            return False
    #__________________________________________________________________
    
    
    #_____________________UPGRADE________________
    
    def upgrade(self):
    
        self.cursor.execute( " SELECT user_id, artist, SUM(scrobbles) as total_scrobbles FROM QUERY GROUP BY user_id, artist")
        out=[]
        out = self.cursor.fetchall()
        #print (out)

        return out

