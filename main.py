import base64
import datetime
import os
import threading
import time

import django
import telebot
from PIL.ImagePalette import random
from django.db.models import Avg
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
from users.state import statistics
import schedule

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
from users.models import User, Status, Ad, Links, State, BotActive
from django.contrib.auth.models import Group

Group.objects.get_or_create(name='бан профиля')
Group.objects.get_or_create(name='изменение профиля')
Group.objects.get_or_create(name='создание аккаунтов')
Group.objects.get_or_create(name='статистика')
Group.objects.get_or_create(name='удаление профиля')
Group.objects.get_or_create(name='управление верефикацией')
Group.objects.get_or_create(name='управление жалобами')
Group.objects.get_or_create(name='управление рекламой')
Group.objects.get_or_create(name='создание рассылок')


@bot.message_handler(commands=['get_photo_id'])
def get_photo_id(message):
    user = User.objects.filter(chat_id=message.chat.id).first()
    user.get_photo_id = True
    user.save(update_fields=['get_photo_id'])
    bot.send_message(user.chat_id, text='Отправляйте фотографии и получайте их ID')


def send_account(user_chat_id):
    markup = types.InlineKeyboardMarkup()
    link = types.InlineKeyboardButton('Аккаунт пользователя', url=f'tg://user?id={user_chat_id}')
    markup.add(link)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = User.objects.filter(chat_id=chat_id).first()
    command = message.text.split()
    if len(command) == 2 and len(command[1].split('_')) == 2 and command[1].split('_')[0] == 'ancete':
        bot.send_message(chat_id=chat_id, text='Ссылка на пользователя',
                         reply_markup=send_account(command[1].split('_')[1]))
    elif len(command) == 2 and len(command[1].split('_')) == 2 and command[1].split('_')[0] == 'link':
        try:
            link, _ = Links.objects.get_or_create(name=command[1].split('_')[1])
        except Exception:
            link = Links.objects.filter(name=command[1].split('_')[1]).first()
        link.user_count += 1
        link.save(update_fields=['user_count'])
    if not user:
        time.sleep(random.uniform(0.1, 1))
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        msg = bot.send_message(chat_id=chat_id, text='Укажи своё имя', reply_markup=None)
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
        msg = bot.send_message(chat_id=chat_id, text='Укажи своё имя', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    elif user.get_photo_id and message.content_type in ['photo', 'video']:
        if message.content_type == 'photo':
            avatar_id = f'photo {message.photo[-1].file_id}'
        else:
            avatar_id = f'video {message.video.file_id}'
        bot.send_message(chat_id=chat_id, text=avatar_id)
    elif user.is_ban:
        bot.send_message(chat_id=chat_id, text='Вы забанены')
    elif user.add_photo == 'step 1':
        registration.add_photo(chat_id=chat_id, message=message)
    elif user.add_photo == 'step 2':
        pass
    else:
        menu(chat_id, user)


def calculate_active_time(user):
    now_time = timezone.now()
    second_time = max(1, int((user.last_active - now_time).timestamp()))
    if second_time < 150:
        user.active_time += second_time
        user.save(update_field=['active_time'])
    user.update_last_active()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    message_id = call.message.id
    chat_id = call.message.chat.id
    user = User.objects.filter(chat_id=call.from_user.id).first()
    username = call.message.from_user.username
    if not user:
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        msg = bot.send_message(chat_id=chat_id, text='Укажи свое имя', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    elif username != user.username:
        user.username = username
        user.save(update_fields=['username'])
    elif user.is_ban:
        bot.send_message(chat_id=chat_id, text='Вы забанены')
    else:
        calculate_active_time(user)
        bot_active, _ = BotActive.objects.get_or_create(
            date=timezone.now().today())
        if user not in bot_active.users:
            bot_active.users.add(user)
        if call.message:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass
            bot.clear_step_handler_by_chat_id(chat_id=chat_id)
            data = call.data.split('|')
            if data[0] == 'menuAfterLike':
                user.add_photo = 'step 3'
                user.save(update_fields=['add_photo'])
                menu(chat_id=chat_id, user=user)
                return

            try:
                if user.delete_message:
                    delete_message = user.delete_message.split(',')
                    for i in delete_message:
                        try:
                            bot.delete_message(chat_id=chat_id, message_id=i)
                        except Exception:
                            pass
                    user.delete_message = ''
                    user.save(update_fields=['delete_message'])
            except Exception as e:
                pass
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
            elif data[0] == 'my_active':
                bot.send_message(chat_id=chat_id, text=f'Статус вашей активности: {user.active_status()}', reply_markup=buttons.go_to_menu())


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
        time.sleep(60 * 60 * 4)


def create_state():
    all_users = User.objects.all()
    users_count = all_users.count()
    ban_users_count = all_users.filter(is_ban=True).count()
    active_users_count = all_users.filter(active=True).count()
    verefi_users_count = all_users.filter(is_checked=True).count()
    female_count = all_users.filter(gender='женский').count()
    male_count = all_users.filter(gender='мужской').count()
    active_female_count = all_users.filter(active=True).filter(gender='женский').count()
    active_male_count = all_users.filter(active=True).filter(gender='мужской').count()
    average_active_time = User.objects.aggregate(Avg('active_time'))['active_time__avg']
    average_active_score = User.objects.aggregate(Avg('active_score'))['active_score__avg']
    file = statistics()
    bot_active, _ = BotActive.objects.get_or_create(
        date=timezone.now().today())
    day_online = bot_active.users.count()
    date = timezone.now().today()
    file.save(f'state/{date}.xlsx')
    State.objects.create(
        users_count=users_count,
        ban_users_count=ban_users_count,
        active_users_count=active_users_count,
        verefi_users_count=verefi_users_count,
        female_count=female_count,
        male_count=male_count,
        active_female_count=active_female_count,
        active_male_count=active_male_count,
        average_active_time=average_active_time,
        average_active_score=average_active_score,
        day_online=day_online
    )
    for user in all_users:
        user.active_time = 0
        if user.is_checked:
            user.active_score = min(0, user.active_score - 15)
        else:
            user.active_score = min(0, user.active_score - 25)
        user.save(update_fields=['active_time', 'active_score'])
    time.sleep(1)


def state():
    schedule.every().day.at("23:59").do(create_state)
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == '__main__':
    polling_thread1 = threading.Thread(target=status)
    polling_thread1.start()
    polling_thread2 = threading.Thread(target=state)
    polling_thread2.start()
    bot.infinity_polling(timeout=50, long_polling_timeout=25)
