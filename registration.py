import os
import random

import django

import buttons
import coord
from const import bot
from menu import menu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
from users.models import User


def create_account(chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id, city, latitude,
                   longitude):
    user = User.objects.create(
        chat_id=chat_id,
        name=name,
        age=age,
        avatar1=avatar_id[0],
        avatar2=avatar_id[1],
        avatar3=avatar_id[2],
        city=city,
        gender=gender,
        category=category,
        description=description,
        find_age=find_age,
        find_gender=find_gender,
        longitude=longitude,
        latitude=latitude,
    )
    menu(chat_id=chat_id, user = user)


def enter_city(message, chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id):
    if message.content_type == 'text':
        city_name = message.text.lower()
        city, latitude, longitude = coord.get_coord_by_name(city_name)
        if not city:
            msg = bot.send_message(chat_id=chat_id, text='Введите верное название города',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender, avatar_id)
        else:
            create_account(chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id, city,
                           latitude, longitude)
    elif message.content_type == 'location':
        latitude = float(message.location.latitude)
        longitude = float(message.location.longitude)
        city, latitude, longitude = coord.get_city_by_coord(latitude=latitude, longitude=longitude)
        if not city:
            msg = bot.send_message(chat_id=chat_id, text='Отправьте верные координаты',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender, avatar_id)
        else:
            create_account(chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id, city,
                           latitude, longitude)
    else:
        msg = bot.send_message(chat_id=chat_id,
                               text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                               reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                       find_gender, avatar_id)


def enter_photo(message, chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id=[None, None, None], n=0):
    if message.content_type == 'photo' and n!=3:
        avatar_id[n] = f'photo {message.photo[-1].file_id}'
        if n == 2:
            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender, avatar_id)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Отправьте еще фотогравию/видео. Если хотите пропустить, нажмите кнопку Пропустить', reply_markup=buttons.skip())
            bot.register_next_step_handler(msg, enter_photo, chat_id, name, age, gender, category, description,
                                           find_age,
                                           find_gender, avatar_id, n+1)
    elif message.content_type == 'video':
        avatar_id[n] = f'video {message.video.file_id}'
        if n == 2:
            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender, avatar_id)
        else:
            msg = bot.send_message(chat_id=chat_id,
                                   text='Отправьте еще фотогравию/видео. Если хотите пропустить, нажмите кнопку Пропустить', reply_markup=buttons.skip())
            bot.register_next_step_handler(msg, enter_photo, chat_id, name, age, gender, category, description,
                                           find_age,
                                           find_gender, avatar_id, n + 1)
    elif message.content_type == 'text' and message.text == 'Пропустить':
        msg = bot.send_message(chat_id=chat_id,
                               text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                               reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                       find_gender, avatar_id)
    else:
        msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию/видео')
        bot.register_next_step_handler(msg, enter_photo, chat_id, name, age, gender, category, description, find_age,
                                       find_gender)


def enter_find_gender(message, chat_id, name, age, gender, category, description, find_age):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери пол, который ищешь из клавиатуры внизу экрана',
                               reply_markup=buttons.find_gender())
        bot.register_next_step_handler(msg, enter_find_gender, chat_id, name, age, gender, category, description,
                                       find_age)
    else:
        find_gender = message.text
        if find_gender not in ['мужской', 'женский', 'любой']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери пол, который ищешь из клавиатуры внизу экрана',
                                   reply_markup=buttons.find_gender())
            bot.register_next_step_handler(msg, enter_find_gender, chat_id, name, age, gender, category, description,
                                           find_age)
        else:
            msg = bot.send_message(chat_id=chat_id,
                                   text='Отправь свою фотографию/видео, которую будут видеть пользователи',
                                   reply_markup=None)
            bot.register_next_step_handler(msg, enter_photo, chat_id, name, age, gender, category, description,
                                           find_age, find_gender)


def get_find_age(age):
    from_age = age - 3
    to_age = age + 3
    if from_age < 16:
        from_age = 16
    if to_age > 100:
        to_age = 99
    return f'{from_age}-{to_age}'


def enter_description(message, chat_id, name, age, gender, category):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напиши о себе(можно пропустить)', reply_markup=buttons.skip())
        bot.register_next_step_handler(msg, enter_description, chat_id, name, age, gender, category)
    else:
        description = message.text
        if description == 'Пропустить':
            description = '🫢🤫'
        ln = len(description)
        if ln > 800:
            msg = bot.send_message(chat_id=chat_id, text=f'Текст должен содержать не более 800 символов. У вас:{ln}',
                                   reply_markup=buttons.skip())
            bot.register_next_step_handler(msg, enter_description, chat_id, name, age, gender, category)
        else:
            find_age = get_find_age(age)
            msg = bot.send_message(chat_id=chat_id, text='Выбери какой пол ты ищешь',
                                   reply_markup=buttons.find_gender())
            bot.register_next_step_handler(msg, enter_find_gender, chat_id, name, age, gender, category, description,
                                           find_age)


def enter_category(message, chat_id, name, age, gender):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери категорию из клавиатуры внизу экрана',
                               reply_markup=buttons.category())
        bot.register_next_step_handler(msg, enter_category, chat_id, name, age, gender)
    else:
        category = message.text
        if category not in ['Серьёзные отношения💞', 'Свободные отношения❤️‍🔥', 'Дружба🫡', 'Не определился🫠']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери категорию из клавиатуры внизу экрана',
                                   reply_markup=buttons.category())
            bot.register_next_step_handler(msg, enter_category, chat_id, name, age, gender)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Напиши о себе(можно пропустить)',
                                   reply_markup=buttons.skip())
            bot.register_next_step_handler(msg, enter_description, chat_id, name, age, gender, category)


def enter_gender(message, chat_id, name, age):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери пол из клавиатуры внизу экрана',
                               reply_markup=buttons.gender())
        bot.register_next_step_handler(msg, enter_gender, chat_id, name, age)
    else:
        gender = message.text
        if gender not in ['мужской', 'женский']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери пол из клавиатуры внизу экрана',
                                   reply_markup=buttons.gender())
            bot.register_next_step_handler(msg, enter_gender, chat_id, name, age)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Выбери для чего ты хочешь использовать бота',
                                   reply_markup=buttons.category())
            bot.register_next_step_handler(msg, enter_category, chat_id, name, age, gender)


def enter_age(message, chat_id, name):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напишите сколько вам лет')
        bot.register_next_step_handler(msg, enter_age, chat_id, name)
    else:
        try:
            age = int(message.text)
            if age < 16 or age > 99:
                raise Exception
        except Exception:
            msg = bot.send_message(chat_id=chat_id, text='Введите число, которое больше 15 и меньше 100')
            bot.register_next_step_handler(msg, enter_age, chat_id, name)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Какой твой пол', reply_markup=buttons.gender())
            bot.register_next_step_handler(msg, enter_gender, chat_id, name, age)


def enter_name(message, chat_id):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напишите как вас зовут')
        bot.register_next_step_handler(msg, enter_name, chat_id)
    else:
        name = message.text
        ln = len(name)
        if ln > 100:
            msg = bot.send_message(chat_id=chat_id, text='Максимальная длина имени 100 символов')
            bot.register_next_step_handler(msg, enter_name, chat_id)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Сколько вам лет?')
            bot.register_next_step_handler(msg, enter_age, chat_id, name)
