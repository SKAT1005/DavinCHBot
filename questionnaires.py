import os

import django

from const import bot
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()







def callback(data, chat_id, user):
    if len(data) == 0:
        pass