# Generated by Django 5.1.1 on 2024-09-21 13:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='фотография')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chat_id', models.CharField(max_length=64, verbose_name='Id чата в телеге')),
                ('name', models.CharField(blank=True, max_length=128, null=True, verbose_name='Имя')),
                ('age', models.IntegerField(blank=True, null=True, verbose_name='Возраст')),
                ('gender', models.CharField(blank=True, max_length=16, null=True, verbose_name='Гендер')),
                ('category', models.CharField(blank=True, max_length=32, null=True, verbose_name='Для чего в боте')),
                ('avatar1', models.CharField(blank=True, max_length=256, null=True, verbose_name='Аватарка пользователя')),
                ('avatar2', models.CharField(blank=True, max_length=256, null=True, verbose_name='Аватарка пользователя')),
                ('avatar3', models.CharField(blank=True, max_length=256, null=True, verbose_name='Аватарка пользователя')),
                ('city', models.CharField(max_length=128, verbose_name='Город')),
                ('check_photo', models.ImageField(blank=True, null=True, upload_to='', verbose_name='Фото для проверки')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание о себе')),
                ('find_age', models.CharField(blank=True, max_length=8, null=True, verbose_name='Какой возраст предпочитает')),
                ('find_gender', models.CharField(blank=True, max_length=16, null=True, verbose_name='Какой гендер ищет')),
                ('latitude', models.FloatField(default=1, verbose_name='Широта')),
                ('longitude', models.FloatField(default=1, verbose_name='Долгота')),
                ('active', models.BooleanField(default=True, verbose_name='Активен ли поиск')),
                ('last_active', models.DateTimeField(default=datetime.datetime(2024, 9, 21, 16, 31, 52, 798262), verbose_name='Время последней активности')),
                ('is_checked', models.BooleanField(default=False, verbose_name='Проеверен ли аккаунт')),
                ('is_admin', models.BooleanField(default=False, verbose_name='Является ли пользователь админом')),
                ('is_ban', models.BooleanField(default=False, verbose_name='В бане ли аккаунт')),
                ('users', models.ManyToManyField(to='users.user', verbose_name='Анкеты, которые подходят под фильтры')),
            ],
        ),
    ]
