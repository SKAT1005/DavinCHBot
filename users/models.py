from django.db import models

class User(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='Id чата в телеге')
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name='Имя')
    age = models.IntegerField(blank=True, null=True, verbose_name='Возраст')
    gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Гендер')
    category = models.CharField(max_length=32, blank=True, null=True, verbose_name='Для чего в боте')
    avatar = models.ImageField(blank=True, null=True, verbose_name='Аватарка пользователя')
    check_photo = models.ImageField(blank=True, null=True, verbose_name='Фото для проверки')
    description = models.TextField(blank=True, null=True, verbose_name='Описание о себе')
    find_age = models.CharField(max_length=8, blank=True, null=True, verbose_name='Какой возраст предпочитает')
    find_gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Какой гендер ищет')
    active = models.BooleanField(default=True, verbose_name='Активен ли поиск')
    is_checked = models.BooleanField(default=False, verbose_name='Проеверен ли аккаунт')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом')
    is_ban = models.BooleanField(default=False, verbose_name='В бане ли аккаунт')

class Image(models.Model):
    image = models.ImageField(verbose_name='фотография')