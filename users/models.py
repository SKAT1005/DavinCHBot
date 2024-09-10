import datetime

from django.db import models
from django.utils import timezone


class User(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='Id чата в телеге')
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name='Имя')
    age = models.IntegerField(blank=True, null=True, verbose_name='Возраст')
    gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Гендер')
    category = models.CharField(max_length=32, blank=True, null=True, verbose_name='Для чего в боте')
    avatar1 = models.CharField(blank=True, max_length=256, null=True, verbose_name='Аватарка пользователя')
    avatar2 = models.CharField(blank=True, max_length=256, null=True, verbose_name='Аватарка пользователя')
    avatar3 = models.CharField(blank=True, max_length=256, null=True, verbose_name='Аватарка пользователя')
    city = models.CharField(max_length=128, verbose_name='Город')
    check_photo = models.ImageField(blank=True, upload_to='verefi', null=True, verbose_name='Фото для проверки')
    description = models.TextField(blank=True, null=True, verbose_name='Описание о себе')
    find_age = models.CharField(max_length=8, blank=True, null=True, verbose_name='Какой возраст предпочитает')
    find_gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Какой гендер ищет')
    latitude = models.FloatField(default=1, verbose_name='Широта')
    longitude = models.FloatField(default=1, verbose_name='Долгота')
    active = models.BooleanField(default=True, verbose_name='Активен ли поиск')
    last_active = models.DateTimeField(default=datetime.datetime.now(), verbose_name='Время последней активности')
    is_checked = models.BooleanField(default=False, verbose_name='Проеверен ли аккаунт')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом')
    is_ban = models.BooleanField(default=False, verbose_name='В бане ли аккаунт')

    def update_last_active(self):
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
    def status(self):
        if self.is_checked:
            return '✅'
        return ''


class Image(models.Model):
    image = models.ImageField(verbose_name='фотография')


class Status(models.Model):
    type = models.CharField(max_length=64, verbose_name='Тип симпатии')
    form_user = models.ForeignKey(User, related_name='to_status', on_delete=models.CASCADE, verbose_name='Человек, который поставил лайк/дизлайк/жалобу')
    to_user = models.ForeignKey(User, related_name='from_status', on_delete=models.CASCADE, verbose_name='Человек, которому поставили лайк/дизлайк/жалобу')
    have_answer = models.BooleanField(default=False, verbose_name='Есть ли взаимность')
    time = models.DateTimeField(auto_now_add=True, verbose_name='Дата симпатии')