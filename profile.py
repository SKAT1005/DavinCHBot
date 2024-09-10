import os
import time

import django
from django.core.files import File

import buttons
from const import bot
from registration import get_city

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()


def edit_photo(message, chat_id, user):
    if message.content_type != 'photo':
        msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию')
        bot.register_next_step_handler(msg, edit_photo, chat_id, user)
    else:
        avatar_id = message.photo[-1].file_id
        file_info = bot.get_file(avatar_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('photo.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
        user.avatar = File(open('photo.jpg', 'rb'))
        user.save(update_fields=['avatar'])
        msg = bot.send_message(chat_id=chat_id, text='Фотография успешно изменена', reply_markup=None)
        bot.delete_message(chat_id=chat_id, message_id=msg.id)
        time.sleep(1.5)
        profile_menu(chat_id=chat_id, user=user)


def edit_city(message, chat_id, user):
    if message.content_type == 'text':
        city = message.text.lower()
        user.city = city
        user.save(update_fields=['city'])
        msg = bot.send_message(chat_id=chat_id, text='Город успешно изменен', reply_markup=None)
        bot.delete_message(chat_id=chat_id, message_id=msg.id)
        time.sleep(1.5)
        profile_menu(chat_id=chat_id, user=user)
    elif message.content_type == 'location':
        city = get_city(message)
        user.city = city
        user.save(update_fields=['city'])
        msg = bot.send_message(chat_id=chat_id, text='Город успешно изменен', reply_markup=None)
        bot.delete_message(chat_id=chat_id, message_id=msg.id)
        time.sleep(1.5)
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
        user.description = description
        user.save(update_fields=['description'])
        msg = bot.send_message(chat_id=chat_id, text='Описание профиля успешно изменене', reply_markup=None)
        bot.delete_message(chat_id=chat_id, message_id=msg.id)
        time.sleep(1.5)
        profile_menu(chat_id=chat_id, user=user)


def edit_age(message, chat_id, user):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напишите сколько вам лет')
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
    else:
        try:
            age = int(message.text)
            if age < 16:
                raise Exception
        except Exception:
            msg = bot.send_message(chat_id=chat_id, text='Введите число, которое больше 16')
            bot.register_next_step_handler(msg, edit_age, chat_id, user)
        else:
            user.age = age
            user.save(update_fields=['age'])
            msg = bot.send_message(chat_id=chat_id, text='Пол поиска изменен')
            bot.delete_message(chat_id=chat_id, message_id=msg.id)
            time.sleep(1.5)
            profile_menu(chat_id=chat_id, user=user)


def profile_menu(chat_id, user):
    text = f'{user.name}, {user.age}, {user.city}, {user.category}\n\n' \
           f'О себе: {user.description}'
    bot.send_photo(chat_id=chat_id, photo=user.avatar, caption=text, reply_markup=buttons.profile_menu())


def callback(data, chat_id, user):
    if len(data) == 0:
        profile_menu(chat_id, user)
    elif data[0] == 'photo':
        msg = bot.send_message(chat_id=chat_id, text='Отправь свою фотографию, которую будут видеть пользователи',
                               reply_markup=None)
        bot.register_next_step_handler(msg, edit_photo, chat_id, user)
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
        msg = bot.send_message(chat_id=chat_id, text='Сколько вам лет?')
        bot.register_next_step_handler(msg, edit_age, chat_id, user)
