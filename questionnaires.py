import os
import random

import django

import buttons
from const import bot
from profile import profile_menu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()


def send_questionnaires(chat_id, user):
    try:
        questionnaire = random.choice(user.users)
    except Exception:
        bot.send_message(chat_id=chat_id,
                         text='К сожалению, анкет, которые подходят к вашим фильтрам нет. Попробуйте обновить ваши фильтры поиска')
    else:
        text = f'{questionnaire.name}, {questionnaire.age}, {questionnaire.city}, {questionnaire.category}\n\n' \
               f'О себе: {questionnaire.description}'
        bot.send_photo(chat_id=questionnaire.chat_id, photo=questionnaire.avatar, caption=text,
                       reply_markup=buttons.questionnaire_menu(questionnaire.chat_id))


def like(chat_id, user, questionnaire_chat_id):
    try:
        text = f'{user.name}, {user.age}, {user.city}, {user.category}\n\n' \
               f'О себе: {user.description}'
        bot.send_message(chat_id=questionnaire_chat_id, text='Ваша заявка понравилась одному человеку')
        bot.send_photo(chat_id=questionnaire_chat_id, photo=user.avatar, caption=text, reply_markup=buttons.answer_on_like(chat_id))
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='Произошла непредвиденная ошибка, мы ее уже решаем',
                         reply_markup=buttons.watch_questionnaire())
def send_message_or_video(message, chat_id, user, questionnaire_chat_id):
    try:
        text = f'{user.name}, {user.age}, {user.city}, {user.category}\n\n' \
               f'О себе: {user.description}'
        bot.send_message(chat_id=questionnaire_chat_id, text='Ваша заявка понравилась одному человеку')
        bot.send_photo(chat_id=questionnaire_chat_id, photo=user.avatar, caption=text, reply_markup=buttons.answer_on_like(chat_id))
    except Exception as e:
        bot.send_message(chat_id=chat_id, text='Произошла непредвиденная ошибка, мы ее уже решаем',
                         reply_markup=buttons.watch_questionnaire())
    else:
        bot.copy_message(chat_id=questionnaire_chat_id, from_chat_id=chat_id, message_id=message.id)

def answer_like(chat_id, user_id):
    bot.send_message(chat_id=chat_id, text='Вы можете продолжить общение в ЛС', reply_markup=buttons.send_link_on_chat(user_id=user_id))
    bot.send_message(chat_id=user_id, text='Вам ответили взаимностью на ваш лайк. Вы можете продолжить общение в ЛС', reply_markup=buttons.send_link_on_chat(user_id=chat_id))

def report(message, chat_id):
    bot.send_message(chat_id=chat_id, text='Спасибо за обращение, мы рассмотрим вашу заявку в ближайшее время')
    #TODO Сделать отправку жалоб в админку

def callback(data, chat_id, user):
    if len(data) == 0:
        send_questionnaires(chat_id=chat_id, user=user)
    elif data[0] == 'like':
        like(chat_id=chat_id, user=user, questionnaire_chat_id=data[1])
    elif data[0] == 'sleep':
        profile_menu(chat_id=chat_id, user=user)
    elif data[0] == 'send_message_or_video':
        msg = bot.send_message(chat_id=chat_id, text='Отправьте сообщение. Это может быть текст, фотография, видео, кружочек или голосовое')
        bot.register_next_step_handler(msg, send_message_or_video, chat_id, user, data[1])
    elif data[0] == 'answer_like':
        answer_like(chat_id=chat_id, user_id=data[1])
    elif data[0] == 'report':
        msg = bot.send_message(chat_id=chat_id, text='Опишити причину вашей жалобы')
        bot.register_next_step_handler(msg, report, chat_id)

