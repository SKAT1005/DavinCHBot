import os
import random

import django
from django.core.files import File

import buttons
from const import bot, simbols

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()

# Import module
from geopy.geocoders import Nominatim
from users.models import User

def get_city(message):
    geolocator = Nominatim(user_agent="my_geocoder")
    Latitude = str(message.location.latitude)
    Longitude = str(message.location.longitude)
    location = geolocator.geocode(Latitude + "," + Longitude)
    city = location.raw['display_name'].split(', ')[-7].lower()
    return city
def enter_check_photo(message, chat_id, user, simbol):
    if message.content_type != 'photo':
        msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию')
        bot.register_next_step_handler(msg, enter_category, chat_id, user)
    else:
        avatar_id = message.photo[-1].file_id
        admin = random.choice(User.objects.filter(is_admin=True))
        text = f'{user.name}, {user.age}, {user.category}\n' \
               f'{user.description}\n\n' \
               f'Жест для проверки: {simbol}'
        bot.send_photo(chat_id=admin.chat_id, photo=avatar_id, caption=text, reply_markup=buttons.check(user.chat_id))


def send_check_photo(chat_id, user):
    simbol = random.choice(simbols)
    text = 'Ваш профиль:\n' \
           f'{user.name}, {user.age}, {user.category}\n' \
           f'{user.description}\n\n' \
           f'Для подтверждения вашего аккаунта, отправьте вашу фотографию, на которой вы показываете следующий символ следующий символ: {simbol}'
    msg = bot.send_photo(chat_id=chat_id, photo=user.avatar, caption=text)
    bot.register_next_step_handler(msg, enter_check_photo, chat_id, user, simbol)


def create_account(chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id, city):
    file_info = bot.get_file(avatar_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('photo.jpg', 'wb') as new_file:
        new_file.write(downloaded_file)
    user = User.objects.create(
        chat_id=chat_id,
        name=name,
        age=age,
        avatar=File(open('photo.jpg', 'rb')),
        city=city,
        gender=gender,
        category=category,
        description=description,
        find_age=find_age,
        find_gender=find_gender
    )
    send_check_photo(chat_id=chat_id, user=user)
    bot.send_message(chat_id=chat_id, text='Ваш аккаунт отправлен на проверку, ожидайте ее результатов')


def enter_city(message, chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id):
    if message.content_type == 'text':
        city = message.text.lower()
        create_account(chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id, city)
    elif message.content_type == 'location':
        city = get_city(message)
        create_account(chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id, city)
    else:
        msg = bot.send_message(chat_id=chat_id,
                               text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой',
                               reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age,
                                       find_gender, avatar_id)
def enter_photo(message, chat_id, name, age, gender, category, description, find_age, find_gender):
    if message.content_type != 'photo':
        msg = bot.send_message(chat_id=chat_id, text='Отправьте фотографию')
        bot.register_next_step_handler(msg, enter_photo, chat_id, name, age, gender, category, description, find_age,
                                       find_gender)
    else:
        avatar_id = message.photo[-1].file_id
        msg = bot.send_message(chat_id=chat_id, text='Введите название вашего города или отправьте координаты, нажав кнопку под клавиатурой', reply_markup=buttons.send_locaton())
        bot.register_next_step_handler(msg, enter_city, chat_id, name, age, gender, category, description, find_age, find_gender, avatar_id)


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
            msg = bot.send_message(chat_id=chat_id, text='Отправь свою фотографию, которую будут видеть пользователи', reply_markup=None)
            bot.register_next_step_handler(msg, enter_photo, chat_id, name, age, gender, category, description,
                                           find_age, find_gender)


def enter_find_age(message, chat_id, name, age, gender, category, description):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Выбери возраст из клавиатуры внизу экрана',
                               reply_markup=buttons.find_age())
        bot.register_next_step_handler(msg, enter_find_age, chat_id, name, age, gender, category, description)
    else:
        find_age = message.text
        if find_age not in ['18-25', '25-35', '45-55', '55-65', '65+']:
            msg = bot.send_message(chat_id=chat_id, text='Выбери возраст из клавиатуры внизу экрана',
                                   reply_markup=buttons.find_age())
            bot.register_next_step_handler(msg, enter_find_age, chat_id, name, age, gender, category, description)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Выбери какой пол ты ищешь',
                                   reply_markup=buttons.find_gender())
            bot.register_next_step_handler(msg, enter_find_gender, chat_id, name, age, gender, category, description,
                                           find_age)


def enter_description(message, chat_id, name, age, gender, category):
    if message.content_type != 'text':
        msg = bot.send_message(chat_id=chat_id, text='Напиши о себе(можно пропустить)', reply_markup=buttons.skip())
        bot.register_next_step_handler(msg, enter_description, chat_id, name, age, gender, category)
    else:
        description = message.text
        if description == 'Пропустить':
            description = '🫢🤫'
        msg = bot.send_message(chat_id=chat_id, text='Выбери, какой возраст ты ищешь', reply_markup=buttons.find_age())
        bot.register_next_step_handler(msg, enter_find_age, chat_id, name, age, gender, category, description)


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
            if age < 18:
                raise Exception
        except Exception:
            msg = bot.send_message(chat_id=chat_id, text='Введите число, которое больше 17')
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
        msg = bot.send_message(chat_id=chat_id, text='Сколько вам лет?')
        bot.register_next_step_handler(msg, enter_age, chat_id, name)
