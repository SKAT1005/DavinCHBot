import os
import time

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
            msg = bot.send_message(chat_id=chat_id, text='Категория поиска изменена')
            bot.delete_message(chat_id=chat_id, message_id=msg.id)
            time.sleep(1.5)
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
            msg = bot.send_message(chat_id=chat_id, text='Пол поиска изменен')
            bot.delete_message(chat_id=chat_id, message_id=msg.id)
            time.sleep(1.5)
            filter_menu(chat_id=chat_id, user=user)


def edit_age(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери возраст из клавиатуры внизу экрана',
                               reply_markup=buttons.find_age())
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    else:
        find_age = message.text
        if find_age not in ['18-25', '25-35', '45-55', '55-65', '65+']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери возраст из клавиатуры внизу экрана',
                                   reply_markup=buttons.find_age())
            bot.register_next_step_handler(msg, edit_age, chat_id, user)
        else:
            user.find_age = find_age
            user.save(update_fields=['find_age'])
            msg = bot.send_message(chat_id=chat_id, text='Возраст поиска изменен')
            bot.delete_message(chat_id=chat_id, message_id=msg.id)
            time.sleep(1.5)
            filter_menu(chat_id=chat_id, user=user)


def filter_menu(chat_id, user):
    text = f'Какой возраст ищем: {user.find_age}\n' \
           f'Какой пол ищем: {user.find_gender}\n' \
           f'Для чего ищем: {user.category}\n'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.filter_menu())


def callback(data, chat_id, user):
    if len(data) == 0:
        filter_menu(chat_id, user)
    elif data[0] == 'age':
        msg = bot.send_message(chat_id=chat_id, text='Выбери, какой возраст ты ищешь', reply_markup=buttons.find_age())
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    elif data[0] == 'gender':
        msg = bot.send_message(chat_id=chat_id, text='Выбери какой пол ты ищешь',
                               reply_markup=buttons.find_gender())
        bot.register_next_step_handler(msg, edit_gender, chat_id, user)
    elif data[0] == 'category':
        msg = bot.send_message(chat_id=chat_id, text='Выбери для чего ты хочешь использовать бота',
                               reply_markup=buttons.category())
        bot.register_next_step_handler(msg, edit_category, chat_id, user)
