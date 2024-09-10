import datetime
import os
import threading
import time

import django
from django.utils import timezone
from telebot import types

import buttons
import filter
import profile
import questionnaires
from const import bot
from registration import enter_name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
from users.models import User, Status


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
    bot.send_media_group(chat_id=chat_id, media=medias)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.menu())


@bot.message_handler(commands=['start'])
def start(message):
    # User.objects.all().delete()
    chat_id = message.chat.id
    print(chat_id)
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        msg = bot.send_message(chat_id=chat_id, text='Напишите как вас зовут', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    else:
        menu(chat_id, user)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    message_id = call.message.id
    chat_id = call.message.chat.id
    user = User.objects.filter(chat_id=call.from_user.id)
    if not user:
        msg = bot.send_message(chat_id=chat_id, text='Напишите как вас зовут', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    else:
        user = user[0]
        user.update_last_active()
        if call.message:
            data = call.data.split('|')
            bot.clear_step_handler_by_chat_id(chat_id=chat_id)
            for i in range(message_id - 3, message_id + 1):
                try:
                    bot.delete_message(chat_id=chat_id, message_id=i)
                except Exception:
                    pass
            if data[0] == 'acept':
                usr = User.objects.get(chat_id=data[1])
                usr.is_checked = True
                usr.save(update_fields=['is_checked'])
                bot.send_message(chat_id=usr.chat_id, text='Ваша анкета одобрена, удачного использования',
                                 reply_markup=None)
            elif data[0] == 'cansel':
                usr = User.objects.get(chat_id=data[1])
                bot.send_message(chat_id=usr.chat_id, text='Ваша анкета не одобрена', reply_markup=None)
            elif data[0] == 'menu':
                menu(chat_id=chat_id, user=user)
            elif data[0] == 'filter':
                filter.callback(data=data[1:], user=user, chat_id=chat_id)
            elif data[0] == 'edit_profile':
                profile.callback(data=data[1:], user=user, chat_id=chat_id)
            elif data[0] == 'profiles':
                if not user.active:
                    user.active = True
                    user.save(update_fields=['active'])
                questionnaires.callback(data=data[1:], user=user, chat_id=chat_id)


def time_menu():
    while True:
        for i in User.objects.all():
            n = i.last_active.timestamp()
            m = datetime.datetime.now().timestamp() - (60*5)
            if n <= m:
                menu(chat_id=i.chat_id, user=i)
                i.last_active = timezone.now() + datetime.timedelta(days=365)
                i.save(update_fields=['last_active'])
            time.sleep(60)


def status():
    while True:
        for i in Status.objects.filter(have_answer=False):
            n = i.time.timestamp()
            if i.type == 'лайк':
                m = (timezone.now() - datetime.timedelta(days=7)).timestamp()
            elif i.type == 'дизлайк':
                m = (timezone.now() - datetime.timedelta(days=1)).timestamp()
            else:
                m = (timezone.now() - datetime.timedelta(days=365)).timestamp()
            if n <= m:
                i.delete()
        time.sleep(60*60*12)


if __name__ == '__main__':
    polling_thread_1 = threading.Thread(target=time_menu)
    polling_thread_1.start()
    polling_thread_2 = threading.Thread(target=status)
    polling_thread_2.start()
    bot.polling(none_stop=True)
