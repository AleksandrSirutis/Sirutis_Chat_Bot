print('in word.py')

import re

#_________Удалим лишние знаки из sentence(запроса пользователя)___
def spacy_tokenizer(sentence):
    
    sentence = re.sub('\'', '', sentence)
    sentence = re.sub('\w*\d\w*', '', sentence)
    sentence = re.sub(' +', ' ', sentence)
    sentence = re.sub(r'\n: \'\'.*', '', sentence)
    sentence = re.sub(r'\n!.*', '', sentence)
    sentence = re.sub(r'^:\'\'.*', '', sentence)
    sentence = re.sub(r'\n', ' ', sentence)
    sentence = re.sub(r'[^\w\s]', ' ', sentence)

    return sentence