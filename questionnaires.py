import datetime
import math
import os
import random
from itertools import chain

import django
from django.utils import timezone
from telebot import types

import buttons
from const import bot
from menu import menu
from profile import profile_menu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()

from users.models import User, Status, LikeUsers, Report, Ad


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
    user_find_gender = [user.gender, 'любой']
    users = User.objects.filter(age__in=age, gender__in=find_gender, category__in=category, active=True,
                                find_gender__in=user_find_gender)
    for usr in users:
        find_age = list(map(int, usr.find_age.split('-')))
        if find_age[0] <= user.age <= find_age[1]:
            if not Status.objects.filter(to_user=usr, form_user=user) and usr != user:
                if is_point_in_circle(latitude=usr.latitude, longitude=usr.longitude,
                                      circle_center_latitude=user.latitude,
                                      circle_center_longitude=user.longitude):
                    return usr
    users = User.objects.filter(age__in=age, gender__in=find_gender, active=True,
                                find_gender__in=user_find_gender)
    for usr in users:
        if not Status.objects.filter(to_user=usr, form_user=user) and usr != user:
            if is_point_in_circle(latitude=usr.latitude, longitude=usr.longitude,
                                  circle_center_latitude=user.latitude,
                                  circle_center_longitude=user.longitude):
                return usr
    return None


def send_ad_photo(ad):
    medias = []
    if ad.photo1:
        medias.append(types.InputMediaPhoto(media=ad.photo1))
    if ad.photo2:
        medias.append(types.InputMediaPhoto(media=ad.photo2))
    if ad.photo3:
        medias.append(types.InputMediaPhoto(media=ad.photo3))
    return medias


def send_questionnaires(chat_id, user):
    n = True
    if random.randint(1, 100) <= 200 and (not user.last_ad_time or user.last_ad_time.timestamp() < (
            timezone.now() - datetime.timedelta(hours=1)).timestamp()):
        try:
            ads = Ad.objects.filter(is_active=True)
            ad_list = []
            for i in ads:
                for n in range(i.chance):
                    ad_list.append(i)
            ad = random.choice(ad_list)
            if ad:
                if ad.end_time and ad.end_time.timestamp() < timezone.now().timestamp():
                    ad.is_active = False
                    ad.save(update_fields=['is_active'])
                    n = False
                else:
                    medias = send_ad_photo(ad)
                    user.last_ad_time = timezone.now()
                    user.delete_message = len(medias)
                    user.save(update_fields=['last_ad_time', 'delete_message'])
                    ad.view += 1
                    if ad.max_view and ad.max_view <= ad.view:
                        ad.is_active = False
                    ad.save(update_fields=['view', 'is_active'])
                    if medias:
                        bot.send_media_group(chat_id=chat_id, media=medias)
                    bot.send_message(chat_id=chat_id, text=ad.text, reply_markup=buttons.watch_questionnaire(), parse_mode='HTML')
                    n = False
            else:
                n = False
        except Exception as e:
            pass
    if n:
        try:
            questionnaire = get_user(user=user)
            if not questionnaire:
                raise Exception
        except Exception as e:
            bot.send_message(chat_id=chat_id,
                             text='К сожалению, подходящие для тебя анкеты закончились. Попробуй обновить фильтры поиска🥹',
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
        msg = bot.send_media_group(chat_id=chat_id, media=medias)
    except Exception:
        pass
    usr = User.objects.get(chat_id=chat_id)
    n = len(medias)
    usr.delete_message = n
    usr.save(update_fields=['delete_message'])
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def send_message_to_questionnaire(questionnaire):
    if not questionnaire.last_like or (
            questionnaire.last_like.timestamp() <= (timezone.now() - datetime.timedelta(minutes=5)).timestamp()):
        text = f'Твоя заявка понравилась {questionnaire.like_users.all().count()} людям'
        bot.send_message(chat_id=questionnaire.chat_id, text=text, reply_markup=buttons.watch_like())
        questionnaire.update_last_like()


def like(chat_id, user, questionnaire_chat_id):
    try:
        questionnaire = User.objects.filter(chat_id=questionnaire_chat_id).first()
        like_user = LikeUsers.objects.create(send_like=user)
        questionnaire.like_users.add(like_user)
        send_message_to_questionnaire(questionnaire=questionnaire)
    except Exception:
        pass
    send_questionnaires(chat_id=chat_id, user=user)


def send_message_or_video(message, chat_id, user, questionnaire_chat_id):
    try:
        questionnaire = User.objects.filter(chat_id=questionnaire_chat_id).first()
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
    else:
        text = 'Мэтчей пока нет🥲'
        bot.send_message(chat_id=questionnaire_chat_id, text=text, reply_markup=buttons.continue_watch())


def answer_like(chat_id, user_id):
    questionnaire = User.objects.filter(chat_id=chat_id).first()
    user = User.objects.filter(chat_id=user_id).first()
    try:
        send_profile(chat_id=chat_id, user=user, markup=None)
        bot.send_message(chat_id=chat_id, text='Вы можете продолжить общение в ЛС',
                         reply_markup=buttons.send_link_on_chat(user_id=user_id))
    except Exception as e:
        pass
    try:
        send_profile(chat_id=user_id, user=questionnaire, markup=None)
        bot.send_message(chat_id=user_id,
                         text='Тебе ответили взаимностью на лайк. Вы можете продолжить общение в ЛС',
                         reply_markup=buttons.send_link_on_chat(user_id=chat_id))
    except Exception as e:
        pass
    for i in questionnaire.like_users.all():
        if i.send_like == user:
            i.delete()
    watch_like(questionnaire_chat_id=chat_id, questionnaire=questionnaire)


def report_step_two(message, chat_id, user, reprot_user, type):
    if message.content_type == 'text':
        bot.send_message(chat_id=chat_id, text='Спасибо за обращение, мы рассмотрим твою заявку в ближайшее время')
        menu(chat_id=chat_id, user=user)
        if user:
            Report.objects.create(reporter=user, user=reprot_user, text=message.text, type=type)
    else:
        msg = bot.send_message(chat_id=chat_id, text='Отправь текст, в котором ты объясняешь причину жалобы')
        bot.register_next_step_handler(msg, report_step_two, chat_id, user, reprot_user, type)


def report_step_one(message, chat_id, user, user_id):
    if message.content_type == 'text' and message.text in ['Нежелательный сексуальный контент🔞', 'Скам, мошенничество',
                                                           'Навязчивая реклама 🤬', 'Оскорбление, буллинг⛔️',
                                                           'Экстремизм, расизм🗿']:
        type = message.text
        report_user = User.objects.filter(chat_id=user_id).first()
        if user:
            msg = bot.send_message(chat_id=chat_id, text='Опиши причину твоей жалобы')
            bot.register_next_step_handler(msg, report_step_two, chat_id, user, report_user, type)
            Report.objects.create(user=report_user, text=message.text)
    else:
        msg = bot.send_message(chat_id=chat_id, text='Отправь текст, в котором ты объясняешь причину жалобы')
        bot.register_next_step_handler(msg, report_step_one, chat_id, user, user_id)


def add_action(type, user, questionnaire_chat_id):
    try:
        to_user = User.objects.filter(chat_id=questionnaire_chat_id).first()
        Status.objects.create(
            form_user=user,
            to_user=to_user,
            type=type
        )
    except Exception:
        pass


def add_answer(user_id, to_user):
    user = User.objects.filter(chat_id=user_id).first()
    Status.objects.get_or_create(
        form_user=user,
        to_user=to_user,
        type='лайк',
        have_answer=True
    )


def answer_dislike(chat_id, user_id):
    questionnaire = User.objects.filter(chat_id=chat_id).first()
    user = User.objects.filter(chat_id=user_id).first()
    for i in questionnaire.like_users.all():
        if i.send_like == user:
            i.delete()
    watch_like(questionnaire_chat_id=chat_id, questionnaire=questionnaire)


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
                               text='Отправь сообщение. Это может быть текст, фотография, видео, кружочек или голосовое')
        bot.register_next_step_handler(msg, send_message_or_video, chat_id, user, data[1])
    elif data[0] == 'answer_like':
        add_action('лайк', user, data[1])
        answer_like(chat_id=chat_id, user_id=data[1])
    elif data[0] == 'answer_dislike':
        add_action('дизлайк', user, data[1])
        answer_dislike(chat_id=chat_id, user_id=data[1])
    elif data[0] == 'report':
        add_action('жалоба', user, data[1])
        msg = bot.send_message(chat_id=chat_id, text='Выбери причину жалобы', reply_markup=buttons.report_type())
        bot.register_next_step_handler(msg, report_step_one, chat_id, user, data[1])
    elif data[0] == 'watch_like':
        watch_like(questionnaire_chat_id=chat_id, questionnaire=user)
