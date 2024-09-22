import os
import random

import django
from django.core.files import File
from telebot import types

import buttons
import coord
from const import bot, simbols

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()


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
        user.save()
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
        user.save()
        photo(chat_id=chat_id, user=user)
    else:
        msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию/видео',
                               reply_markup=buttons.go_back('edit_profile|photo'))
        bot.register_next_step_handler(msg, edit_photo, chat_id, user)


def edit_city(message, chat_id, user):
    if message.content_type == 'text':
        name = message.text.lower()
        city, latitude, longitude = coord.get_coord_by_name(name)
        if not city:
            msg = bot.send_message(chat_id=chat_id, text='Введите верное название города',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, edit_city, chat_id, user)
        else:
            user.city = city
            user.latitude = latitude
            user.longitude = longitude
            user.is_checked = False
            user.save(update_fields=['city', 'latitude', 'longitude', 'is_checked'])
            profile_menu(chat_id=chat_id, user=user)
    elif message.content_type == 'location':
        latitude = float(message.location.latitude)
        longitude = float(message.location.longitude)
        city, latitude, longitude = coord.get_city_by_coord(latitude=latitude, longitude=longitude)
        if not city:
            msg = bot.send_message(chat_id=chat_id, text='Отправьте верные координаты',
                                   reply_markup=buttons.send_locaton())
            bot.register_next_step_handler(msg, edit_city, chat_id, user)
        else:
            user.city = city
            user.latitude = latitude
            user.longitude = longitude
            user.is_checked = False
            user.save(update_fields=['city', 'latitude', 'longitude', 'is_checked'])
            profile_menu(chat_id=chat_id, user=user)
    else:
        msg = bot.send_message(chat_id=chat_id,
                               text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                               reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, edit_city, chat_id, user)


def edit_description(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напиши о себе(можно пропустить)', reply_markup=buttons.skip())
        bot.register_next_step_handler(msg, edit_description, chat_id, user)
    else:
        description = message.text
        if description == 'Пропустить':
            description = '🫢🤫'
        ln = len(description)
        if ln > 800:
            msg = bot.send_message(chat_id=chat_id, text=f'Текст должен содержать не более 800 символов. У вас:{ln}',
                                   reply_markup=buttons.skip())
            bot.register_next_step_handler(msg, edit_description, chat_id, user)
        else:
            user.description = description
            user.save(update_fields=['description'])
            profile_menu(chat_id=chat_id, user=user)


def edit_age(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напишите сколько вам лет',
                               reply_markup=buttons.go_back('edit_profile'))
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    else:
        try:
            age = int(message.text)
            if age < 16:
                raise Exception
        except Exception:
            msg = bot.send_message(chat_id=chat_id, text='Введите число, которое больше 16',
                                   reply_markup=buttons.go_back('edit_profile'))
            bot.register_next_step_handler(msg, edit_age, chat_id, user)
        else:
            user.age = age
            user.is_checked = False
            user.save(update_fields=['age', 'is_checked'])
            profile_menu(chat_id=chat_id, user=user)


def profile_menu(chat_id, user):
    text = f'{user.status()} {user.name}, {user.age}, {user.city}, {user.category}\n\n' \
           f'О себе: {user.description}'
    medias = []
    if user.avatar1:
        medias = add_media(medias, user.avatar1)
    if user.avatar2:
        medias = add_media(medias, user.avatar2)
    if user.avatar3:
        medias = add_media(medias, user.avatar3)
    bot.send_media_group(chat_id=chat_id, media=medias)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.profile_menu())


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
                     reply_markup=buttons.edit_photo())


def verefi(message, chat_id, user, simbol):
    if not user.is_checked:
        if message.content_type != 'photo':
            msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию')
            bot.register_next_step_handler(msg, verefi, chat_id, user)
        else:
            avatar_id = message.photo[-1].file_id
            file_info = bot.get_file(avatar_id)
            downloaded_file = bot.download_file(file_info.file_path)
            path = f'verefi.jpg'
            with open(path, 'wb') as new_file:
                new_file.write(downloaded_file)
            user.check_photo = File(open(path, 'rb'))
            user.save(update_fields=['check_photo'])
            profile_menu(chat_id=chat_id, user=user)
    else:
        bot.send_message(chat_id=chat_id, text='Ваша анкета уже верефицирована', reply_markup=buttons.go_to_menu())


def edit_name(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напишите как вас зовут',
                               reply_markup=buttons.go_back('edit_profile'))
        bot.register_next_step_handler(msg, edit_name, chat_id, user)
    else:
        name = message.text
        ln = len(name)
        if ln > 100:
            msg = bot.send_message(chat_id=chat_id, text='Максимальная длина имени 100 символов',
                                   reply_markup=buttons.go_back('edit_profile'))
            bot.register_next_step_handler(msg, edit_name, chat_id, user)
        else:
            user.name = name
            user.save(update_fields=['name'])
            profile_menu(chat_id=chat_id, user=user)

def edit_gender(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери пол из клавиатуры внизу экрана',
                               reply_markup=buttons.gender())
        bot.register_next_step_handler(msg, edit_gender, chat_id, user)
    else:
        gender = message.text
        if gender not in ['мужской', 'женский']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери пол из клавиатуры внизу экрана',
                                   reply_markup=buttons.gender())
            bot.register_next_step_handler(msg, edit_gender, chat_id, user)
        else:
            user.gender = gender
            user.save(update_fields=['name'])
            profile_menu(chat_id=chat_id, user=user)


def callback(data, chat_id, user):
    if len(data) == 0:
        profile_menu(chat_id, user)
    elif data[0] == 'photo':
        photo(chat_id=chat_id, user=user)
    elif data[0] == 'edit_photo':
        msg = bot.send_message(chat_id=chat_id, text='Отправь свою фотографию/видео, которую будут видеть пользователи',
                               reply_markup=buttons.go_back('edit_profile'))
        bot.register_next_step_handler(msg, edit_photo, chat_id, user, data[-1])
    elif data[0] == 'city':
        msg = bot.send_message(chat_id=chat_id,
                               text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                               reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, edit_city, chat_id, user)
    elif data[0] == 'description':
        msg = bot.send_message(chat_id=chat_id, text='Напиши о себе(можно пропустить)',
                               reply_markup=buttons.skip())
        bot.register_next_step_handler(msg, edit_description, chat_id, user)
    elif data[0] == 'age':
        msg = bot.send_message(chat_id=chat_id, text='Сколько вам лет?', reply_markup=buttons.go_back('edit_profile'))
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    elif data[0] == 'go_sleep':
        user.active = False
        user.save(update_fields=['active'])
        profile_menu(chat_id=chat_id, user=user)
    elif data[0] == 'delite':
        user.delete()
        bot.send_message(chat_id=chat_id, text='Ваша анкета удалена', reply_markup=buttons.create())
    elif data[0] == 'verefi':
        simbol = random.choice(simbols)
        text = f'Для подтверждения вашего аккаунта, отправьте вашу фотографию, на которой вы показываете следующий символ следующий символ: {simbol}'
        msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.go_back('edit_profile'))
        bot.register_next_step_handler(msg, verefi, chat_id, user, simbol)
    elif data[0] == 'name':
        msg = bot.send_message(chat_id=chat_id, text='Напишите как вас зовут', reply_markup=None)
        bot.register_next_step_handler(msg, edit_name, chat_id, user)
    elif data[0] == 'gender':
        msg = bot.send_message(chat_id=chat_id, text='Какой твой пол', reply_markup=buttons.gender())
        bot.register_next_step_handler(msg, edit_gender, chat_id, user)
