print('in model.py')

import pandas as pd
import numpy as np


from scipy import sparse
from sklearn.preprocessing import normalize

async def compile_model():

    interactions_df = pd.read_csv('lastfm_user_scrobbles.csv', encoding='utf-8')
    titles_df = pd.read_csv('lastfm_artist_list.csv', encoding='utf-8')
#    interactions_df = pd.read_csv('updated_lastfm_user_scrobbles.csv', encoding='utf-8')
#    titles_df = pd.read_csv('updated_lastfm_artist_list.csv', encoding='utf-8')

    # Конвертируем датафрейм в словарь, что бы удобно было получать по индексу исполнителя его имя
    titles_df.index = titles_df['artist_id']
    title_dict = titles_df['artist_name'].to_dict()
    titles_df['artist_name'] = titles_df['artist_name'].str.strip()
    #

    # Получаем в первой переменной сами индексы юзеров, а во второй позиции юзеров в данном датафрейме 
    rows, r_pos = np.unique(interactions_df.values[:,0], return_inverse=True)

    # Получаем в первой переменной сами индексы артистов(исполнителей), а во второй позиции артистов(исполнителей) 
    # в данном датафрейме 
    cols, c_pos = np.unique(interactions_df.values[:,1], return_inverse=True)

    # Сконструируем sparse матрицу. Значащие значения из третьей колонки(это количество прослушиваний).
    interactions_sparse = sparse.csr_matrix((interactions_df.values[:,2], (r_pos, c_pos)))
    #print(interactions_sparse)

    '''
    Так как количество просмотров данных исполнителей от 1 до тысяч для разных исполнителей, то
    нормализуем данные, используя L2 норму.
    Посчитаем матрицу похожести исполнителей на исполнителей. ))
    Для наших исполнителей можно посчитать близость по юзерам.
    ИЗ преобразованной транспонированной и преобразованной матриц получаем матрицу,
    в ячейках которой будут косинусные расстояния между наших исполнителей!!!!
    '''
    Pui = normalize(interactions_sparse, norm='l2', axis=1)
    #print(Pui)
    sim = Pui.T * Pui
    #print(sim)
    '''
    Получаем из матрицы нужную нам строчку, конвертируем её в массив, забираем функцией(argsort) 
    отсортированный список аргументов и берём посление 10 (так, как нужно 10 похожих по максимальным просмотрам).
    Это будут самые близкие к нашему выбранному индексу исполнителя (id_artist) индексы других исполнителей.

    [title_dict[+1] for i in sim [id_artist].toarray().argsort()[0][-10:]]

    '''

    # Код для наладки
    '''
    # Извлекаем строку с id_artist и преобразуем ее в массив numpy
    artist_row_test = sim[9866].toarray()[0]
    # Получаем список id наиболее похожих исполнителей (кроме самого исполнителя)
    similar_artist_ids_test = np.argsort(-artist_row_test)[1:11]
    # Получаем список имен наиболее похожих исполнителей
    similar_artist_names_test = [title_dict[x] for x in similar_artist_ids_test]
    #print(type(sim))
    print(similar_artist_names_test)
    '''

    print('Модель создана из функции, и обнавлены данные')
    #print(title_dict)
    
    return title_dict, sim  

interactions_df = pd.read_csv('lastfm_user_scrobbles.csv', encoding='utf-8')
titles_df = pd.read_csv('lastfm_artist_list.csv', encoding='utf-8')

# Конвертируем датафрейм в словарь, что бы удобно было получать по индексу исполнителя его имя
titles_df.index = titles_df['artist_id']
title_dict = titles_df['artist_name'].to_dict()
titles_df['artist_name'] = titles_df['artist_name'].str.strip()
#

# Получаем в первой переменной сами индексы юзеров, а во второй позиции юзеров в данном датафрейме 
rows, r_pos = np.unique(interactions_df.values[:,0], return_inverse=True)

# Получаем в первой переменной сами индексы артистов(исполнителей), а во второй позиции артистов(исполнителей) в данном датафрейме 
cols, c_pos = np.unique(interactions_df.values[:,1], return_inverse=True)

# Сконструируем sparse матрицу. Значащие значения из третьей колонки(это количество прослушиваний).
interactions_sparse = sparse.csr_matrix((interactions_df.values[:,2], (r_pos, c_pos)))
#print(interactions_sparse)

'''
    Так как количество просмотров данных исполнителей от 1 до тысяч для разных исполнителей, то
    нормализуем данные, используя L2 норму.
    Посчитаем матрицу похожести исполнителей на исполнителей. ))
    Для наших исполнителей можно посчитать близость по юзерам.
    ИЗ преобразованной транспонированной и преобразованной матриц получаем матрицу,
в ячейках которой будут косинусные расстояния между наших исполнителей!!!!
'''
Pui = normalize(interactions_sparse, norm='l2', axis=1)
#print(Pui)
sim = Pui.T * Pui
#print(sim)
'''
    Получаем из матрицы нужную нам строчку, конвертируем её в массив, забираем функцией(argsort) 
отсортированный список аргументов и берём посление 10 (так, как нужно 10 похожих по максимальным просмотрам).
Это будут самые близкие к нашему выбранному индексу исполнителя (id_artist) индексы других исполнителей.

[title_dict[+1] for i in sim [id_artist].toarray().argsort()[0][-10:]]

'''

# Код для наладки
'''
# Извлекаем строку с id_artist и преобразуем ее в массив numpy
artist_row_test = sim[9866].toarray()[0]
# Получаем список id наиболее похожих исполнителей (кроме самого исполнителя)
similar_artist_ids_test = np.argsort(-artist_row_test)[1:11]
# Получаем список имен наиболее похожих исполнителей
similar_artist_names_test = [title_dict[x] for x in similar_artist_ids_test]
#print(type(sim))
print(similar_artist_names_test)
'''


#interactions_sparse_transposed = interactions_sparse.transpose(copy=True)
#Piu = normalize(interactions_sparse_transposed, norm='l2', axis=1)

#fit = Pui * Piu * Pui

#print('размерность матрицы fit = ',fit.shape)

#aaa1 = [title_dict[+1] for i in np.nonzero(interactions_sparse[520])[1].tolist()]
#print (aaa1)
#

print('Модель создана')

#______________ПОДБОР АРТИСТОВ_________________________
async def find_similar_artists(artist):     # Наиболее слушаемые артисты вместе с текущим артистом 
    print('Для артиста "', artist, '"подберём артистов.')   # для наладки
    
    artist_id=None                          # обнулим
    for key, value in title_dict.items():   # пройдёмся по словарю
        if value == artist:                 # если это наш артист, то
            artist_id = key                 # сохраним его id

    # Этот код для проверки при наладке
    if artist_id is not None:
                print('id артиста - ', artist_id)
    else: 
                print('id артиста не найдено')
    #----------------------------------
    
    if artist_id is not None:   # Если артист найден в каталоге
        # Извлекаем строку с id_artist и преобразуем ее в массив numpy
        artist_row = sim[artist_id].toarray()[0] 
        # Получаем список id наиболее похожих исполнителей (кроме самого исполнителя)
        similar_artist_ids = np.argsort(-artist_row)[1:11]
        # Получаем список имен наиболее похожих исполнителей
        similar_artist_names = [title_dict[x] for x in similar_artist_ids]   
        
        print('C артистом ', artist, ', часто слушают следующих артистов: ',similar_artist_names)
        return similar_artist_names
    
    else:               # Если не нашли артиста, 
        return False    # то выдадим ошибку
    
