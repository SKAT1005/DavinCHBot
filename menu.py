import os

import django
from telebot import types

import buttons
from const import bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
def add_media(medias, avatar_data):
    type, media_id = avatar_data.split()
    if type == 'photo':
        medias.append(types.InputMediaPhoto(media=media_id))
    else:
        medias.append(types.InputMediaVideo(media=media_id))
    return medias
def menu(chat_id, user):
    text = f'{user.status()} {user.name}, {user.age}, {user.city}, {user.category}\n\n' \
           f'О себе: {user.description}'
    medias = []
    if user.avatar1:
        medias = add_media(medias, user.avatar1)
    if user.avatar2:
        medias = add_media(medias, user.avatar2)
    if user.avatar3:
        medias = add_media(medias, user.avatar3)
    try:
        bot.send_media_group(chat_id=chat_id, media=medias)
    except Exception:
        print(chat_id)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.menu())