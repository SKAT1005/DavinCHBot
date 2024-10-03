import base64
import datetime
import os
import threading
import time

import django
import telebot
from PIL.ImagePalette import random
from django.utils import timezone
from telebot import types

import buttons
import filter
import profile
import random
import questionnaires
import registration
from const import bot
from menu import menu
from registration import enter_name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
from users.models import User, Status


@bot.message_handler(commands=['start'])
def start(message):
    # КUser.objects.all().delete()
    chat_id = message.chat.id
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        time.sleep(random.uniform(0.1, 1))
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        msg = bot.send_message(chat_id=chat_id, text='Укажи своё имя.', reply_markup=None)
        bot.register_next_step_handler_by_chat_id(chat_id, enter_name, chat_id)
    elif user.is_ban:
        bot.send_message(chat_id=chat_id, text='Вы забанены')
    elif user.add_photo == 'step 1':
        registration.add_photo(chat_id=chat_id, message=message)
    elif user.add_photo == 'step 2':
        pass
    else:
        menu(chat_id, user)

@bot.message_handler(content_types=telebot.util.content_type_media)
def answer_on_message(message):
    chat_id = message.chat.id
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        time.sleep(random.uniform(0.1, 1))
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        msg = bot.send_message(chat_id=chat_id, text='Укажи своё имя.', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    elif user.is_ban:
        bot.send_message(chat_id=chat_id, text='Вы забанены')
    elif user.add_photo == 'step 1':
        registration.add_photo(chat_id=chat_id, message=message)
    elif user.add_photo == 'step 2':
        pass
    else:
        menu(chat_id, user)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    message_id = call.message.id
    chat_id = call.message.chat.id
    user = User.objects.filter(chat_id=call.from_user.id)
    if not user:
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        msg = bot.send_message(chat_id=chat_id, text='Укажи свое имя', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    elif user[0].is_ban:
        bot.send_message(chat_id=chat_id, text='Вы забанены')
    else:
        user = user[0]
        # user.update_last_active()
        if call.message:
            data = call.data.split('|')
            bot.clear_step_handler_by_chat_id(chat_id=chat_id)
            # for i in range(message_id - 4, message_id + 1):
            #     try:
            #         bot.delete_message(chat_id=chat_id, message_id=i)
            #     except Exception:
            #         pass
            msg = bot.send_message(chat_id=chat_id, text='.', reply_markup=types.ReplyKeyboardRemove())
            bot.delete_message(chat_id=chat_id, message_id=msg.id)
            if data[0] == 'menu':
                user.add_photo = 'step 3'
                user.save(update_fields=['add_photo'])
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
            elif data[0] == 'first_edit_photo':
                msg = bot.send_message(chat_id=chat_id, text='Отправь фотографию/видео',
                                       reply_markup=buttons.go_back('edit_profile|photo'))
                bot.register_next_step_handler(msg, registration.edit_photo, chat_id, user, data[1])


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
    polling_thread = threading.Thread(target=status)
    polling_thread.start()
    bot.polling(none_stop=True)
