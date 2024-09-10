from telebot import types


def gender():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    male = types.KeyboardButton('мужской')
    female = types.KeyboardButton('женский')
    markup.add(male, female)
    return markup


def category():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    category1 = types.KeyboardButton('свидание')
    category2 = types.KeyboardButton('дружба')
    category3 = types.KeyboardButton('общение')
    category4 = types.KeyboardButton('серьезные отношения')
    category5 = types.KeyboardButton('пока не определился')
    category6 = types.KeyboardButton('онлайн общение')
    markup.add(category1, category2, category3, category4, category5, category6)
    return markup


def skip():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    skip = types.KeyboardButton('Пропустить')
    markup.add(skip)
    return markup


def find_age():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    age1 = types.KeyboardButton('18-25')
    age2 = types.KeyboardButton('25-35')
    age3 = types.KeyboardButton('45-55')
    age4 = types.KeyboardButton('55-65')
    age5 = types.KeyboardButton('65+')
    markup.add(age1, age2, age3, age4, age5)
    return markup


def find_gender():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    male = types.KeyboardButton('мужской')
    female = types.KeyboardButton('женский')
    all = types.KeyboardButton('любой')
    markup.add(male, female, all)
    return markup

def check(id):
    markup = types.InlineKeyboardMarkup()
    acept = types.InlineKeyboardButton('Одобрить', callback_data=f'acept|{id}')
    cansel = types.InlineKeyboardButton('Отказать', callback_data=f'cansel|{id}')
    markup.add(acept, cansel)
    return markup
