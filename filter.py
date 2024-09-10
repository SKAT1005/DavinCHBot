import math
import os
import time

import django

import buttons
from buttons import category, find_gender, gender
from const import bot
from users.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()

def update_users(user):
    find_age = list(map(int, user.find_age.split('-')))
    category = [user.category]
    if category[0] == 'Не определился🫠':
        category = ['Серьёзные отношения💞', 'Свободные отношения❤️‍🔥', 'Дружба🫡', 'Не определился🫠']
    find_gender = [user.gender]
    if find_gender[0] == 'любой':
        find_gender = ['мужской', 'женский']
    gender = [user.gender, 'любой']
    users = User.objects.filter(category__in=category, age__in=find_age, gender__in=find_gender, find_gender__in=gender)
    for usr in users:
        if is_point_in_circle(latitude=usr.latitude, longitude=usr.longitude, circle_center_latitude=user.latitude, circle_center_longitude=user.longitude):
            from_age, to_age = map(int, usr.find_age.split('-'))
            if from_age<=user.age<=to_age:
                user.users.add(usr)
                user.save(update_fields=['users'])

def is_point_in_circle(latitude, longitude, circle_center_latitude, circle_center_longitude, radius_km=5):

  # Преобразуем углы в радианы
  latitude = math.radians(latitude)
  longitude = math.radians(longitude)
  circle_center_latitude = math.radians(circle_center_latitude)
  circle_center_longitude = math.radians(circle_center_longitude)

  # Вычисляем расстояние между точкой и центром круга по формуле Гаверсинуса
  distance_km = 2 * 6371 * math.asin(math.sqrt(
      math.sin((circle_center_latitude - latitude) / 2)**2 +
      math.cos(circle_center_latitude) * math.cos(latitude) *
      math.sin((circle_center_longitude - longitude) / 2)**2
  ))

  # Сравниваем расстояние с радиусом
  return distance_km <= radius_km

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
            update_users(user)
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
            update_users(user)
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
            update_users(user)
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
