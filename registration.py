import os
import random
import time

import django
from telebot import types

import buttons
import coord
from const import bot
from menu import menu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
from users.models import User


def create_account(chat_id, name, age, gender, category, description, find_age, find_gender, city, latitude,
                   longitude):
    User.objects.create(
        chat_id=chat_id,
        name=name,
        age=age,
        city=city,
        gender=gender,
        category=category,
        description=description,
        find_age=find_age,
        find_gender=find_gender,
        longitude=longitude,
        latitude=latitude,
    )
    bot.send_message(chat_id=chat_id, text='Отправьте нам до трех своих фотографий')

def edit_photo(message, chat_id, user, number):
    if message.content_type == 'photo':
        avatar_id = f'photo {message.photo[-1].file_id}'
        if number == '1':
            user.avatar1 = avatar_id
        elif number == '2':
            user.avatar2 = avatar_id
        else:
            user.avatar3 = avatar_id
        user.is_checked = False
        user.save(update_fields=['avatar1', 'avatar2', 'avatar3'])
        photo(chat_id=chat_id, user=user)
    elif message.content_type == 'video':
        avatar_id = f'video {message.video.file_id}'
        if number == '1':
            user.avatar1 = avatar_id
        elif number == '2':
            user.avatar2 = avatar_id
        else:
            user.avatar3 = avatar_id
        user.is_checked = False
        user.save(['avatar1', 'avatar2', 'avatar3'])
        photo(chat_id=chat_id, user=user)
    else:
        msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию/видео',
                               reply_markup=buttons.go_back('edit_profile|photo'))
        bot.register_next_step_handler(msg, edit_photo, chat_id, user, number)
def add_media(medias, avatar_data):
    type, media_id = avatar_data.split()
    if type == 'photo':
        medias.append(types.InputMediaPhoto(media=media_id))
    else:
        medias.append(types.InputMediaVideo(media=media_id))
    return medias


def photo(chat_id, user):
    medias = []
    if user.avatar1:
        medias = add_media(medias, user.avatar1)
    if user.avatar2:
        medias = add_media(medias, user.avatar2)
    if user.avatar3:
        medias = add_media(medias, user.avatar3)
    bot.send_media_group(chat_id=chat_id, media=medias)
    bot.send_message(chat_id=chat_id, text='Выберите какую фотографию/видео хотите поменять',
                     reply_markup=buttons.first_edit_photo())

def add_photo(chat_id, message):
    content_type = message.content_type
    if content_type in ['photo', 'video']:
        if content_type == 'photo':
            avatar_id = f'photo {message.photo[-1].file_id}'
        else:
            avatar_id = f'video {message.video.file_id}'
        time.sleep(random.uniform(0.00001, 0.005))
        user = User.objects.get(chat_id=chat_id)
        if not user.avatar1:
            user.avatar1 += f'{avatar_id}'
            user.save(update_fields=['avatar1'])
            bot.send_message(chat_id=chat_id, text='Добавлена 1/3 фотографий. Отправьте еще или перейдите к просмотру, нажав кнопку под клавиатурой', reply_markup=buttons.watch_photo())
        elif not user.avatar2:
            user.avatar2 = avatar_id
            user.save(update_fields=['avatar2'])
            bot.send_message(chat_id=chat_id, text='Добавлена 2/3 фотографий. Отправьте еще или перейдите к просмотру, нажав кнопку под клавиатурой',
                             reply_markup=buttons.watch_photo())
        elif not user.avatar3:
            user.avatar3 = avatar_id
            user.add_photo = 'step 2'
            user.save(update_fields=['avatar3', 'add_photo'])
            photo(chat_id=chat_id, user=user)

    else:
        if user.avatar1 and content_type == 'text' and message.text == 'Смотреть мои фотографии':
            user.add_photo = 'step 2'
            user.save(update_fields=['add_photo'])
            photo(chat_id=chat_id, user=user)
        else:
            if user.avatar2:
                bot.send_message(chat_id=chat_id,
                                 text='Добавлена 2/3 фотографий. Отправьте еще или перейдите к просмотру, нажав кнопку под клавиатурой',
                                 reply_markup=buttons.watch_photo())
            elif user.avatar1:
                bot.send_message(chat_id=chat_id,
                                 text='Добавлена 1/3 фотографий. Отправьте еще или перейдите к просмотру, нажав кнопку под клавиатурой',
                                 reply_markup=buttons.watch_photo())
            else:
                bot.send_message(chat_id=chat_id, text='Отправьте нам до трех своих фотографий')



def enter_city(message, chat_id, name, age, gender, category, description, find_age, find_gender):
    if message.content_type == 'text':
        city_name = message.text.lower()
        city, latitude, longitude = coord.get_coord_by_name(city_name)
        if not city:
            msg = bot.send_message(chat_id=chat_id, text='Введите верное название города',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender)
        else:
            create_account(chat_id, name, age, gender, category, description, find_age, find_gender, city,
                           latitude, longitude)
    elif message.content_type == 'location':
        latitude = float(message.location.latitude)
        longitude = float(message.location.longitude)
        city, latitude, longitude = coord.get_city_by_coord(latitude=latitude, longitude=longitude)
        if not city:
            msg = bot.send_message(chat_id=chat_id, text='Отправьте верные координаты',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender)
        else:
            create_account(chat_id, name, age, gender, category, description, find_age, find_gender, city,
                           latitude, longitude)
    else:
        msg = bot.send_message(chat_id=chat_id,
                               text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                               reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
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
                                   text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                           find_gender)


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
