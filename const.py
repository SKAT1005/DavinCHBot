import os

import django
from telebot import TeleBot, apihelper

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
# django.setup()
# from django.contrib.auth.models import Group

API_TOKEN = '7171194252:AAGyTNMYCDdA-Zb3jvz5qVCFS0Qfwaf_ieo'

bot = TeleBot(API_TOKEN)

simbols = '🤙👌🤘🤟✌️'

# Group.objects.get_or_create(name='бан профиля')
# Group.objects.get_or_create(name='изменение профиля')
# Group.objects.get_or_create(name='создание аккаунтов')
# Group.objects.get_or_create(name='статистика')
# Group.objects.get_or_create(name='удаление профиля')
# Group.objects.get_or_create(name='управление верефикацией')
# Group.objects.get_or_create(name='управление жалобами')
# Group.objects.get_or_create(name='управление рекламой')
