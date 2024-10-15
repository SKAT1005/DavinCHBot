import os

import django
from telebot import TeleBot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()

bot = TeleBot('7071542790:AAGLBF9X6V-PDSqcJAPXkfaHBvFR8haowu0')

simbols = '🤙👌🤘🤟✌️'

