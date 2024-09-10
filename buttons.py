from telebot import types


def gender():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    male = types.KeyboardButton('мужской')
    female = types.KeyboardButton('женский')
    markup.add(male, female)
    return markup


def category():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    category1 = types.KeyboardButton('Серьёзные отношения💞')
    category2 = types.KeyboardButton('Свободные отношения❤️‍🔥')
    category3 = types.KeyboardButton('Дружба🫡')
    category4 = types.KeyboardButton('Не определился🫠')
    markup.add(category1, category2, category3, category4)
    return markup


def send_locaton():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    locaton = types.KeyboardButton('Моя локация', request_location=True)
    markup.add(locaton)
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



def menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    watch = types.InlineKeyboardButton('Смотреть анкты', callback_data='profiles')
    edit_filter = types.InlineKeyboardButton('Настроить поиск', callback_data='filter')
    edit_profile = types.InlineKeyboardButton('Настроить анкету', callback_data='edit_profile')
    markup.add(watch, edit_filter, edit_profile)
    return markup


def filter_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    edit_age = types.InlineKeyboardButton('Изменить возраст поиска', callback_data='filter|age')
    edit_gender = types.InlineKeyboardButton('Изменить пол поиска', callback_data='filter|gender')
    edit_category = types.InlineKeyboardButton('Изменить категорию поиска', callback_data='filter|category')
    menu = types.InlineKeyboardButton('Вернуться назад', callback_data='menu')
    markup.add(edit_age, edit_gender, edit_category, menu)
    return markup



def profile_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    edit_avatar = types.InlineKeyboardButton('Изменить фотографию', callback_data='edit_profile|photo')
    edit_city = types.InlineKeyboardButton('Изменить город', callback_data='edit_profile|city')
    edit_description = types.InlineKeyboardButton('Изменить описание', callback_data='edit_profile|description')
    edit_age = types.InlineKeyboardButton('Изменить возраст', callback_data='edit_profile|age')
    menu = types.InlineKeyboardButton('Вернуться назад', callback_data='menu')
    markup.add(edit_age, edit_avatar, edit_city, edit_description, menu)
    return markup