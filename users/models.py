import base64

from django.contrib.auth.models import User as main_user
from django.db import models
from django.utils import timezone
from const import bot


class User(models.Model):
    chat_id = models.CharField(max_length=64, blank=True, null=True, verbose_name='Id чата в телеге')
    name = models.CharField(max_length=128, blank=True, null=True, verbose_name='Имя')
    username = models.CharField(max_length=128, default='', blank=True, null=True, verbose_name='Ник пользователя')
    age = models.IntegerField(blank=True, null=True, verbose_name='Возраст')
    gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Гендер')
    category = models.CharField(max_length=32, blank=True, null=True, verbose_name='Для чего в боте')
    avatars = models.ManyToManyField('Photo', blank=True, verbose_name='Аватарки')
    city = models.CharField(max_length=128, blank=True, null=True, verbose_name='Город')
    check_photo = models.ForeignKey('Photo', on_delete=models.CASCADE, related_name='user_check_photo', blank=True, null=True, verbose_name='Фото для верефикации')
    check_simbol = models.CharField(max_length=8, blank=True, null=True, verbose_name='Символ для верефикации')
    need_verefi = models.BooleanField(default=False, verbose_name='Требуется ли верефикация')
    description = models.TextField(blank=True, null=True, verbose_name='Описание о себе')
    find_age = models.CharField(max_length=8, blank=True, null=True, verbose_name='Какой возраст предпочитает')
    find_gender = models.CharField(max_length=16, blank=True, null=True, verbose_name='Какой гендер ищет')
    latitude = models.FloatField(default=1, verbose_name='Широта')
    longitude = models.FloatField(default=1, verbose_name='Долгота')
    active = models.BooleanField(default=False, verbose_name='Активен ли поиск')
    delete_message = models.TextField(blank=True, null=True, verbose_name='Сколько сообщений удалить?')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    like_users = models.ManyToManyField('LikeUsers', blank=True,
                                        verbose_name='Пользователи, которые лайкнули анкету')
    last_active = models.DateTimeField(default=None, null=True, verbose_name='Время последней активности')
    active_time = models.IntegerField(default=0, verbose_name='Время активности в боте за последние 24 часа')
    active_score = models.FloatField(default=50, verbose_name='Баллы активности в боте')
    last_ad_time = models.DateTimeField(default=None, null=True, verbose_name='Время просмотра последней рекламы')
    last_like = models.DateTimeField(default=None, null=True, verbose_name='Время последней отправки сообщения о лайках')
    is_checked = models.BooleanField(default=False, verbose_name='Проеверен ли аккаунт')
    is_fake = models.BooleanField(default=False, verbose_name='Фейковая ли анкета?')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом')
    is_ban = models.BooleanField(default=False, verbose_name='В бане ли аккаунт')
    add_photo = models.CharField(max_length=16, default='step 1', verbose_name='Добавляют ли фото')
    get_photo_id = models.BooleanField(default=False, verbose_name='Получает ли пользователь id фотографий?')



    def active_status(self):
        if self.active_score < 25:
            return 'Не активен'
        elif self.active_score < 50:
            return 'Низкая активность'
        elif self.active_score < 75:
            return 'Средняя активность'
        else:
            return 'Высокая активность'

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
            try:
                type, file_id = self.file_id.split()
                file_info = bot.get_file(file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                encoded_string = base64.b64encode(downloaded_file).decode('utf-8')
                self.base64_file = encoded_string
                self.save(update_fields=['base64_file'])
            except Exception:
                return None
        return self.base64_file

    def get_type(self):
        return self.file_id.split()[0]



class Report(models.Model):
    reporter = models.ForeignKey(User, related_name='reporters', on_delete=models.CASCADE, verbose_name='Пользователь, который подал жалобу')
    user = models.ForeignKey(User, related_name='reports', on_delete=models.CASCADE, verbose_name='Пользователь, на которого подана жалоба')
    text = models.TextField(verbose_name='Текст жалобы')
    type = models.CharField(max_length=128, verbose_name='Причина жалобы')


class Ad(models.Model):
    photo1 = models.ImageField(upload_to='photos', blank=True, null=True, verbose_name='Фотография рекламы1')
    photo2 = models.ImageField(upload_to='photos', blank=True, null=True, verbose_name='Фотография рекламы2')
    photo3 = models.ImageField(upload_to='photos', blank=True, null=True, verbose_name='Фотография рекламы3')
    text = models.TextField(verbose_name='Текст рекламы')
    view = models.IntegerField(default=0, verbose_name='Количество показов')
    max_view = models.IntegerField(default=None, blank=True, null=True, verbose_name='Нужное кол-во показов')
    chance = models.IntegerField(default=5, verbose_name='Шанс показа в процентах')
    start_time = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Время начала показа')
    end_time = models.DateTimeField(default=None, blank=True, null=True, verbose_name='Время конца показа')
    is_active = models.BooleanField(default=False, verbose_name='Активна ли реклама')


    def status(self):
        if self.is_active:
            return 'Активна'
        return 'Не активна'


class Logs(models.Model):
    type = models.CharField(max_length=2048, verbose_name='Тип Действия')
    user = models.ForeignKey(main_user, related_name='logs', on_delete=models.CASCADE, verbose_name='Пользователь, который совершает действие')
    time = models.DateTimeField(verbose_name='Время действия')


class Links(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название ссылки')
    user_count = models.IntegerField(default=0, verbose_name='Количество пользователей')


class BotActive(models.Model):
    date = models.DateField(verbose_name='Дата')
    users = models.ManyToManyField('User', blank=True, on_delete=models.PROTECT, related_name='zxc', verbose_name='Пользователи')


class State(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name='Дата статистики')
    users_count = models.IntegerField(verbose_name='Кол-во пользователей')
    ban_users_count = models.IntegerField(verbose_name='Кол-во забаненых анкет')
    active_users_count = models.IntegerField(verbose_name='Кол-во активных анкет')
    verefi_users_count = models.IntegerField(verbose_name='Кол-во подтвержденных')
    female_count = models.IntegerField(verbose_name='Кол-во женщин')
    male_count = models.IntegerField(verbose_name='Кол-во мужчин')
    active_male_count = models.IntegerField(verbose_name='Кол-во активных мужских аккаунтов')
    active_female_count = models.IntegerField(verbose_name='Кол-во активных женских аккаунтов')
    average_active_time = models.IntegerField(verbose_name='Среднее время активности в боте')
    average_active_score = models.IntegerField(verbose_name='Средний бал активности в боте')
    day_online = models.IntegerField(verbose_name='Сколько людей пользовалось ботом')
    file = models.FileField(verbose_name='Файл полной статистики')