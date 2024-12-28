import os

import django
from telebot import TeleBot, apihelper

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()

API_TOKEN = '7171194252:AAGyTNMYCDdA-Zb3jvz5qVCFS0Qfwaf_ieo'

bot = TeleBot(API_TOKEN)

simbols = '🤙👌🤘🤟✌️'

