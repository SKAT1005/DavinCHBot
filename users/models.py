import base64
import datetime

from django.db import models
from django.utils import timezone
from const import bot


class User(models.Model):
    chat_id = models.CharField(max_length=64, blank=True, null=True, verbose_name='Id чата в телеге')
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name='Имя')
    age = models.IntegerField(blank=True, null=True, verbose_name='Возраст')
    gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Гендер')
    category = models.CharField(max_length=32, blank=True, null=True, verbose_name='Для чего в боте')
    avatars = models.ManyToManyField('Photo', blank=True, null=True, verbose_name='Аватарки')
    city = models.CharField(max_length=128, blank=True, null=True, verbose_name='Город')
    check_photo = models.ImageField(blank=True, upload_to='verefi', null=True, verbose_name='Фото для проверки')
    description = models.TextField(blank=True, null=True, verbose_name='Описание о себе')
    find_age = models.CharField(max_length=8, blank=True, null=True, verbose_name='Какой возраст предпочитает')
    find_gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Какой гендер ищет')
    latitude = models.FloatField(default=1, verbose_name='Широта')
    longitude = models.FloatField(default=1, verbose_name='Долгота')
    active = models.BooleanField(default=True, verbose_name='Активен ли поиск')
    like_users = models.ManyToManyField('LikeUsers', blank=True, null=True,
                                        verbose_name='Пользователи, которые лайкнули анкету')
    last_active = models.DateTimeField(default=timezone.now(), verbose_name='Время последней активности')
    last_like = models.DateTimeField(default=timezone.now(), verbose_name='Время последней отправки сообщения о лайках')
    is_checked = models.BooleanField(default=False, verbose_name='Проеверен ли аккаунт')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом')
    is_ban = models.BooleanField(default=False, verbose_name='В бане ли аккаунт')
    add_photo = models.CharField(max_length=16, default='step 1', verbose_name='Добавляют ли фото')

    def update_last_active(self):
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])

    def update_last_like(self):
        self.last_like = timezone.now()
        self.save(update_fields=['last_like'])

    def status(self):
        if self.is_checked:
            return '✅'
        return ''
    def check_verefi(self):
        if self.is_checked:
            return 'Верефицирован'
        return 'Не верефицирован'

    def check_ban(self):
        if self.is_ban:
            return 'Забанен'
        else:
            return 'Не забанен'


class Image(models.Model):
    image = models.ImageField(verbose_name='фотография')


class Status(models.Model):
    type = models.CharField(max_length=64, verbose_name='Тип симпатии')
    form_user = models.ForeignKey(User, related_name='to_status', on_delete=models.CASCADE,
                                  verbose_name='Человек, который поставил лайк/дизлайк/жалобу')
    to_user = models.ForeignKey(User, related_name='from_status', on_delete=models.CASCADE,
                                verbose_name='Человек, которому поставили лайк/дизлайк/жалобу')
    have_answer = models.BooleanField(default=False, verbose_name='Есть ли взаимность')
    time = models.DateTimeField(auto_now_add=True, verbose_name='Дата симпатии')


class LikeUsers(models.Model):
    send_like = models.ForeignKey(User, related_name='send_like', on_delete=models.CASCADE)
    message_id = models.CharField(max_length=512, blank=True, null=True, verbose_name='ID сообщения')

class Photo(models.Model):
    file_id = models.CharField(blank=True, default='', max_length=256, null=True,
                               verbose_name='Аватарка пользователя 1')
    base64_file = models.TextField(blank=True, null=True, verbose_name='Файл в формате base64')

    def get_data(self):
        if not self.base64_file:
            type, file_id = self.file_id.split()
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            encoded_string = base64.b64encode(downloaded_file).decode('utf-8')
            self.base64_file = encoded_string
            self.save(update_fields=['base64_file'])
        return self.base64_file

    def get_type(self):
        return self.file_id.split()[0]

