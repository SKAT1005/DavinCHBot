import datetime
import math
import os
from itertools import chain

import django
from django.utils import timezone
from telebot import types

import buttons
from const import bot
from profile import profile_menu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()

from users.models import User, Status, LikeUsers


def is_point_in_circle(latitude, longitude, circle_center_latitude, circle_center_longitude, radius_km=100):
    # Преобразуем углы в радианы
    latitude = math.radians(latitude)
    longitude = math.radians(longitude)
    circle_center_latitude = math.radians(circle_center_latitude)
    circle_center_longitude = math.radians(circle_center_longitude)

    # Вычисляем расстояние между точкой и центром круга по формуле Гаверсинуса
    distance_km = 2 * 6371 * math.asin(math.sqrt(
        math.sin((circle_center_latitude - latitude) / 2) ** 2 +
        math.cos(circle_center_latitude) * math.cos(latitude) *
        math.sin((circle_center_longitude - longitude) / 2) ** 2
    ))

    # Сравниваем расстояние с радиусом
    return distance_km <= radius_km


def get_user(user):
    from_age, to_age = map(int, user.find_age.split('-'))
    age = [i for i in range(from_age, to_age + 1)]
    category = [user.category]
    find_gender = [user.find_gender]
    if category[0] == 'Не определился🫠':
        category = ['Серьёзные отношения💞', 'Свободные отношения❤️‍🔥', 'Дружба🫡', 'Не определился🫠']
    if find_gender[0] == 'любой':
        find_gender = ['мужской', 'женский']
    users = User.objects.filter(age__in=age, gender__in=find_gender, category__in=category, active=True)
    for usr in users:
        if not Status.objects.filter(to_user=usr, form_user=user) and usr != user:
            if is_point_in_circle(latitude=usr.latitude, longitude=usr.longitude, circle_center_latitude=user.latitude,
                                  circle_center_longitude=user.longitude):
                return usr
    users = User.objects.filter(age__in=age, gender__in=find_gender, active=True)
    for usr in users:
        if not Status.objects.filter(to_user=usr, form_user=user) and usr != user:
            if is_point_in_circle(latitude=usr.latitude, longitude=usr.longitude, circle_center_latitude=user.latitude,
                                  circle_center_longitude=user.longitude):
                return usr
    return None


def send_questionnaires(chat_id, user):
    try:
        questionnaire = get_user(user=user)
        if not questionnaire:
            raise Exception
    except Exception as e:
        bot.send_message(chat_id=chat_id,
                         text='К сожалению, анкет, которые подходят к вашим фильтрам нет. Попробуйте обновить ваши фильтры поиска',
                         reply_markup=buttons.go_to_menu())
    else:
        send_profile(chat_id, questionnaire, buttons.questionnaire_menu(questionnaire.chat_id))


def add_media(medias, avatar_data):
    type, media_id = avatar_data.split()
    if type == 'photo':
        medias.append(types.InputMediaPhoto(media=media_id))
    else:
        medias.append(types.InputMediaVideo(media=media_id))
    return medias


def send_profile(chat_id, user, markup):
    text = f'{user.status()} {user.name}, {user.age}, {user.city}, {user.category}\n\n' \
           f'О себе: {user.description}'
    medias = []
    for i in user.avatars.all()[:3]:
        medias = add_media(medias, i.file_id)
    try:
        bot.send_media_group(chat_id=chat_id, media=medias)
    except Exception:
        pass
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def send_message_to_questionnaire(questionnaire):
    if questionnaire.last_like.timestamp() <= (timezone.now() - datetime.timedelta(minutes=5)).timestamp():
        text = f'Ваша заявка понравилась {questionnaire.like_users.all().count()} людям'
        bot.send_message(chat_id=questionnaire.chat_id, text=text, reply_markup=buttons.watch_like())
        questionnaire.update_last_like()


def like(chat_id, user, questionnaire_chat_id):
    try:
        questionnaire = User.objects.get(chat_id=questionnaire_chat_id)
        like_user = LikeUsers.objects.create(send_like=user)
        questionnaire.like_users.add(like_user)
        send_message_to_questionnaire(questionnaire=questionnaire)
    except Exception:
        pass
    send_questionnaires(chat_id=chat_id, user=user)


def send_message_or_video(message, chat_id, user, questionnaire_chat_id):
    try:
        questionnaire = User.objects.get(chat_id=questionnaire_chat_id)
        like_user = LikeUsers.objects.create(send_like=user, message_id=message.id)
        questionnaire.like_users.add(like_user)
        send_message_to_questionnaire(questionnaire=questionnaire)
    except Exception:
        pass
    send_questionnaires(chat_id=chat_id, user=user)


def watch_like(questionnaire_chat_id, questionnaire):
    if questionnaire.like_users.all():
        like = questionnaire.like_users.first()
        user = like.send_like
        send_profile(questionnaire_chat_id, user, buttons.answer_on_like(user.chat_id))
        if like.message_id:
            try:
                bot.copy_message(chat_id=questionnaire_chat_id, from_chat_id=user.chat_id, message_id=like.message_id)
            except Exception:
                pass
        like.delete()
    else:
        text = 'У вас закончились анкеты, которые вас лайкнули :('
        bot.send_message(chat_id=questionnaire_chat_id, text=text, reply_markup=buttons.continue_watch())


def answer_like(chat_id, user_id):
    try:
        bot.send_message(chat_id=chat_id, text='Вы можете продолжить общение в ЛС',
                         reply_markup=buttons.send_link_on_chat(user_id=user_id))
    except Exception:
        pass
    try:
        bot.send_message(chat_id=user_id,
                         text='Вам ответили взаимностью на ваш лайк. Вы можете продолжить общение в ЛС',
                         reply_markup=buttons.send_link_on_chat(user_id=chat_id))
    except Exception:
        pass
    questionnaire = User.objects.get(chat_id=chat_id)
    watch_like(questionnaire_chat_id=chat_id, questionnaire=questionnaire)


def report(message, chat_id):
    bot.send_message(chat_id=chat_id, text='Спасибо за обращение, мы рассмотрим вашу заявку в ближайшее время')
    # TODO Сделать отправку жалоб в админку


def add_action(type, user, questionnaire_chat_id):
    try:
        to_user = User.objects.get(chat_id=questionnaire_chat_id)
        Status.objects.create(
            form_user=user,
            to_user=to_user,
            type=type
        )
    except Exception:
        pass


def add_answer(user_id, to_user):
    user = User.objects.get(chat_id=user_id)
    Status.objects.get_or_create(
        form_user=user,
        to_user=to_user,
        type='лайк',
        have_answer=True
    )


def callback(data, chat_id, user):
    if len(data) == 0:
        send_questionnaires(chat_id=chat_id, user=user)
    elif data[0] == 'like':
        add_action('лайк', user, data[1])
        like(chat_id=chat_id, user=user, questionnaire_chat_id=data[1])
    elif data[0] == 'dislike':
        add_action('дизлайк', user, data[1])
        send_questionnaires(chat_id=chat_id, user=user)
    elif data[0] == 'sleep':
        profile_menu(chat_id=chat_id, user=user)
    elif data[0] == 'send_message_or_video':
        add_action('лайк', user, data[1])
        msg = bot.send_message(chat_id=chat_id,
                               text='Отправьте сообщение. Это может быть текст, фотография, видео, кружочек или голосовое')
        bot.register_next_step_handler(msg, send_message_or_video, chat_id, user, data[1])
    elif data[0] == 'answer_like':
        add_action('лайк', user, data[1])
        answer_like(chat_id=chat_id, user_id=data[1])
    elif data[0] == 'answer_like':
        add_action('дизлайк', user, data[1])
        watch_like(questionnaire_chat_id=chat_id, questionnaire=user)
    elif data[0] == 'report':
        add_action('жалоба', user, data[1])
        msg = bot.send_message(chat_id=chat_id, text='Опишите причину вашей жалобы')
        bot.register_next_step_handler(msg, report, chat_id)
    elif data[0] == 'watch_like':
        watch_like(questionnaire_chat_id=chat_id, questionnaire=user)
