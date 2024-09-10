import os

import django

import buttons
import filter
import profile
import questionnaires
from const import bot
from registration import enter_name, send_check_photo

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
from users.models import User


def menu(chat_id, user):
    text = f'{user.name}, {user.age}, {user.city}, {user.category}\n\n' \
           f'О себе: {user.description}'
    bot.send_photo(chat_id=chat_id, photo=user.avatar, caption=text, reply_markup=buttons.menu())


@bot.message_handler(commands=['start'])
def start(message):
    # User.objects.all().delete()
    chat_id = message.chat.id
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        msg = bot.send_message(chat_id=chat_id, text='Напишите как вас зовут', reply_markup=None)
        bot.register_next_step_handler(msg, enter_name, chat_id)
    elif not user.is_checked:
        bot.send_message(chat_id=chat_id, text='Ваша анкета на проверке, ожидайте', reply_markup=None)
    elif user.is_checked:
        menu(chat_id, user)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    message_id = call.message.id
    chat_id = call.message.chat.id
    user, _ = User.objects.get_or_create(chat_id=call.from_user.id)
    if call.message:
        data = call.data.split('|')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
        if data[0] == 'acept':
            usr = User.objects.get(chat_id=data[1])
            usr.is_checked = True
            usr.save(update_fields=['is_checked'])
            bot.send_message(chat_id=usr.chat_id, text='Ваша анкета одобрена, удачного использования', reply_markup=None)
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
            questionnaires.callback(data=data[1:], user=user, chat_id=chat_id)


bot.polling(none_stop=True)
