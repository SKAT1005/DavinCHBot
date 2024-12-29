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
from users.models import User, Status, Ad, Links
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
    txt = """
    <b>1. Объединение стилей: Стили из обоих исходных файлов были объединены в один блок. Некоторые дублирующиеся стили, такие как font-family, margin, padding были перенесены в глобальные стили body и container.</b>
<i>2. Применение стилей:
   - Добавлены стили для textarea  height: 200px
   - Добавлены стили для кнопок форматирования
   - Обновлены стили для textarea</i>
<u>3. Внедрение редактора: HTML-редактор был внедрен в форму, путем добавления textarea и кнопок для форматирования текста. Так же добавлено поле preview для просмотра</u>
<strike>4. Изменение id: id textarea с htmlInput был изменен на text</strike>
<span class="tg-spoiler">5. Адаптированный JS: JavaScript был адаптирован для работы с новым id textarea.</span>
<a href="http://www.example.com/">6. Добавление type=button: для кнопок форматирования
</a>
<pre class="language-python">Особенности:

•   Единый стиль: Весь код использует единый стиль оформления.
•   Форматирование текста: Внедрены кнопки форматирования текста.
•   Предварительный просмотр: Возможность предпросмотра введенного текста с HTML-тегами.
•   Адаптация: JS-код адаптирован к новым id и классам элементов.
•   Организация кода: Код разбит на логические блоки.
</pre>
<code>Теперь код имеет единый стиль, а функциональность редактора HTML-текста встроена в форму создания рекламы.</code>
    """
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text=txt, parse_mode='HTML')
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
        # user.update_last_active()
        if call.message:
            bot.clear_step_handler_by_chat_id(chat_id=chat_id)
            data = call.data.split('|')
            if data[0] == 'menuAfterLike':
                user.add_photo = 'step 3'
                user.save(update_fields=['add_photo'])
                menu(chat_id=chat_id, user=user)
                return

            try:
                message_ids = []
                for i in range(user.delete_message + 1):
                    message_ids.append(message_id - i)
                for message_id in message_ids:
                    bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
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


def ad_check():
    while True:
        for ad in Ad.objects.filter(is_active=True):
            if ad.deactivate_time.timestamp() >= timezone.now():
                ad.is_active = False
                ad.save(update_fields=['is_active'])
        time.sleep(60 * 60)


if __name__ == '__main__':
    polling_thread1 = threading.Thread(target=status)
    polling_thread1.start()
    polling_thread2 = threading.Thread(target=ad_check)
    polling_thread2.start()
    bot.infinity_polling(timeout=50, long_polling_timeout=25)
