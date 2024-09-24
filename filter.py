import os

import django

import buttons
from const import bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()




def edit_category(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери категорию из клавиатуры внизу экрана',
                               reply_markup=buttons.category())
        bot.register_next_step_handler(msg, edit_category, chat_id, user)
    else:
        category = message.text
        if category not in ['Серьёзные отношения💞', 'Свободные отношения❤️‍🔥', 'Дружба🫡', 'Не определился🫠']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери категорию из клавиатуры внизу экрана',
                                   reply_markup=buttons.category())
            bot.register_next_step_handler(msg, edit_category, chat_id, user)
        else:
            user.category = category
            user.save(update_fields=['category'])
            filter_menu(chat_id=chat_id, user=user)


def edit_gender(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери пол, который ищешь из клавиатуры внизу экрана',
                               reply_markup=buttons.find_gender())
        bot.register_next_step_handler(msg, edit_gender, chat_id, user)
    else:
        find_gender = message.text
        if find_gender not in ['мужской', 'женский', 'любой']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери пол, который ищешь из клавиатуры внизу экрана',
                                   reply_markup=buttons.find_gender())
            bot.register_next_step_handler(msg, edit_gender, chat_id, user)
        else:
            user.find_gender = find_gender
            user.save(update_fields=['find_gender'])
            filter_menu(chat_id=chat_id, user=user)


def edit_age(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери подходящий возраст:\n'
                                                     'От … До …\n'
                                                     '(Запиши оба числа без пробелов)🌞🌚\n'
                                                     'Пример: 1825', reply_markup=buttons.go_back('filter'))
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    else:
        try:
            find_age = int(message.text)
        except Exception:
            msg = bot.send_message(chat_id=chat_id, text='Введи число в формате от.. до.. без пробелов',
                               reply_markup=buttons.go_back('filter'))
            bot.register_next_step_handler(msg, edit_age, chat_id, user)
        else:
            from_age = find_age//100
            to_age = find_age%100
            if from_age < 16 or to_age >99:
                msg = bot.send_message(chat_id=chat_id, text='Числа должны лежать в диапазоне от 16 до 99',
                               reply_markup=buttons.go_back('filter'))
                bot.register_next_step_handler(msg, edit_age, chat_id, user)
            elif from_age>to_age:
                msg = bot.send_message(chat_id=chat_id, text='Первые два числа должны быть меньше',
                               reply_markup=buttons.go_back('filter'))
                bot.register_next_step_handler(msg, edit_age, chat_id, user)
            else:
                user.find_age = f'{from_age}-{to_age}'
                user.save(update_fields=['find_age'])
                filter_menu(chat_id=chat_id, user=user)


def filter_menu(chat_id, user):
    text = f'Возрастная категория: {user.find_age}\n' \
           f'Пол собеседника:  {user.find_gender}\n' \
           f'Цель общения: {user.category}\n'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.filter_menu())


def callback(data, chat_id, user):
    if len(data) == 0:
        filter_menu(chat_id, user)
    elif data[0] == 'age':
        msg = bot.send_message(chat_id=chat_id, text='Выбери подходящий возраст:\n'
                                                     'От … До …\n'
                                                     '(Запиши оба числа без пробелов)🌞🌚\n'
                                                     'Пример: 1825', reply_markup=buttons.go_back('filter'))
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    elif data[0] == 'gender':
        msg = bot.send_message(chat_id=chat_id, text='Выбери пол собеседника😏',
                               reply_markup=buttons.find_gender())
        bot.register_next_step_handler(msg, edit_gender, chat_id, user)
    elif data[0] == 'category':
        msg = bot.send_message(chat_id=chat_id, text='Выбери цель общения😊',
                               reply_markup=buttons.category())
        bot.register_next_step_handler(msg, edit_category, chat_id, user)