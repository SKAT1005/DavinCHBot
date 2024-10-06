import random

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import Q, Count
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.utils import timezone
from django.views import View

from buttons import questionnaire_menu
from const import bot
from coord import get_coord_by_name
from users.models import User, Report, Ad, Photo, Logs

def create_logs(user, action):
    Logs.objects.create(user=user, type=action, time=timezone.now())
def user_view(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    if request.method == 'GET':
        filter = Q()
        sorting = request.GET.get('sorting')
        age = request.GET.get('age')
        gender = request.GET.get('gender')
        city = request.GET.get('city')
        category = request.GET.get('category')
        description = request.GET.get('description')

        # Обработка возраста
        try:
            if age:
                if '-' in age:
                    filter &= Q(age__range=list(map(int, age.split('-'))))
                else:
                    filter &= Q(age=int(age))
        except Exception:
            pass

        # Фильтрация по другим параметрам
        if gender:
            filter &= Q(gender=gender)
        if city:
            filter &= Q(city=city)
        if category:
            filter &= Q(category=category)
        if description == 'нет':
            filter &= Q(description='🫢🤫')
        elif description == 'да':
            filter &= ~Q(description='🫢🤫')

        # Запрос пользователей с сортировкой и подсчетом лайков
        users = User.objects.annotate(like_users_count=Count('like_users'))
        if filter:
            users = users.filter(filter)
        if sorting:
            users = users.order_by(sorting)

            # Получение уникальных городов
        unique_cities = User.objects.values_list('city', flat=True).distinct()

        return render(request, 'user_list.html', {'users': users, 'citys': unique_cities})


def delete_profile(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='удаление профиля'):
        return HttpResponseRedirect('/profiles')
    try:
        user = User.objects.get(id=pk)
        reports = Report.objects.filter(user=user)
        create_logs(request.user, f'Удаление профиля {user.chat_id}')
        if reports:
            reports.delete()
        user.delete()
    except Exception:
        pass
    return HttpResponseRedirect('/profiles')


def ban_profile(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='бан профиля'):
        return HttpResponseRedirect('/profiles')
    try:
        user = User.objects.get(id=pk)
        create_logs(request.user, f'Бан профиля {user.chat_id}')
        reports = Report.objects.filter(user=user)
        if reports:
            reports.delete()
        user.is_ban = not user.is_ban
        user.active = not user.is_ban
        user.is_checked = False
        user.save(update_fields=['is_ban', 'active', 'is_checked'])
    except Exception as e:
        pass
    return HttpResponseRedirect('/profiles')


class EditProfile(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        elif not request.user.groups.filter(name='изменение профиля'):
            return HttpResponseRedirect('/profiles')
        try:
            user = User.objects.get(id=pk)
            return render(request, 'edit_profile.html', context={'user': user})
        except Exception:
            return HttpResponseRedirect('/profiles')

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        elif not request.user.groups.filter(name='изменение профиля'):
            return HttpResponseRedirect('/profiles')
        try:
            user = User.objects.get(id=pk)
            create_logs(request.user, f'Изменение профиля {user.chat_id}')
            description = request.POST.get('description')
            user.description = description
            user.save(update_fields=['description'])
            return render(request, 'edit_profile.html', context={'user': user})
        except Exception:
            return HttpResponseRedirect('/profiles')


def stat(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='статистика'):
        return HttpResponseRedirect('/profiles')
    all_users = User.objects.all()
    users_count = all_users.count()
    ban_users_count = all_users.filter(is_ban=True).count()
    active_users_count = all_users.filter(active=True).count()
    verefi_users_count = all_users.filter(active=True).count()
    female_count = all_users.filter(gender='женский').count()
    male_count = all_users.filter(gender='мужской').count()
    active_female_count = all_users.filter(active=True, gender='женский').count()
    active_male_count = all_users.filter(active=True, gender='мужской').count()
    return render(request, 'stat.html', context={
        'users_count': users_count,
        'ban_users_count': ban_users_count,
        'active_users_count': active_users_count,
        'verefi_users_count': verefi_users_count,
        'female_count': female_count,
        'male_count': male_count,
        'active_female_count': active_female_count,
        'active_male_count': active_male_count
    })


def verefi(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление верефикацией'):
        return HttpResponseRedirect('/profiles')
    users = User.objects.filter(need_verefi=True)
    return render(request, 'verefi.html', context={'users': users})


def acept_verefi(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление верефикацией'):
        return HttpResponseRedirect('/profiles')
    try:
        user = User.objects.get(id=pk)
        create_logs(request.user, f'Подтверждение верефикации профиля {user.chat_id}')
        bot.send_message(chat_id=user.chat_id, text='Вам одобрена верификация')
        user.is_checked = True
        user.need_verefi = False
        user.check_photo = None
        user.check_simbol = None
        user.save(update_fields=['is_checked', 'need_verefi', 'check_photo', 'check_simbol'])
    except Exception:
        pass
    return HttpResponseRedirect('/verefi')


def cansel_verefi(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление верефикацией'):
        return HttpResponseRedirect('/profiles')
    try:
        user = User.objects.get(id=pk)
        create_logs(request.user, f'отказ верефикации профиля {user.chat_id}')
        bot.send_message(chat_id=user.chat_id, text='Вам отказана верификация')
        user.is_checked = False
        user.need_verefi = False
        user.check_photo = None
        user.check_simbol = None
        user.save(update_fields=['is_checked', 'need_verefi', 'check_photo', 'check_simbol'])
    except Exception:
        pass
    return HttpResponseRedirect('/verefi')


def report(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление жалобами'):
        return HttpResponseRedirect('/profiles')
    reports = Report.objects.all()
    return render(request, 'reports.html', context={'reports': reports})


def cansel_report(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление жалобами'):
        return HttpResponseRedirect('/profiles')
    try:
        Report.objects.get(id=pk).delete()
    except Exception:
        pass
    return HttpResponseRedirect('/reports')


def ad_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление рекламой'):
        return HttpResponseRedirect('/profiles')
    ads = Ad.objects.all()
    return render(request, 'ad.html', context={'ads': ads})


def create_ad(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление рекламой'):
        return HttpResponseRedirect('/profiles')
    if request.method == 'POST':
        create_logs(request.user, f'Создание рекламы')
        photo = request.FILES.get('image')
        text = request.POST.get('text')
        try:
            Ad.objects.create(photo=photo, text=text)
        except Exception as e:
            pass
        return HttpResponseRedirect('/ad')
    else:
        return render(request, 'create_ad.html')


def delete_ad(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление рекламой'):
        return HttpResponseRedirect('/profiles')
    try:
        create_logs(request.user, f'Удаление рекламы')
        Ad.objects.get(id=pk).delete()
    except Exception:
        pass
    return HttpResponseRedirect('/ad')


def deactivate_ad(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='управление рекламой'):
        return HttpResponseRedirect('/profiles')
    try:
        create_logs(request.user, f'Активация/деактивация рекламы')
        ad = Ad.objects.get(id=pk)
        ad.is_active = not ad.is_active
        ad.save(update_fields=['is_active'])
    except Exception:
        pass
    return HttpResponseRedirect('/ad')


def create_account(request, name, gender, seeking, age, city, category, description, photo1, photo2, photo3):
    n = True
    if len(name) > 100:
        messages.error(request, f'Длина имени должна быть меньше 100 символов. У вас {len(name)} символов')
        n = False
    if len(description) > 100:
        messages.error(request, f'Длина описания должна быть меньше 800 символов. У вас {len(description)} символов')
        n = False
    if photo1 and photo1.split()[0] not in ['photo', 'video']:
        n = False
        messages.error(request, 'Фотография должна быть в формате [photo/video file_id]')
    if photo2 and photo2.split()[0] not in ['photo', 'video']:
        messages.error(request, 'Фотография должна быть в формате [photo/video file_id]')
        n = False
    if photo3 and photo3.split()[0] not in ['photo', 'video']:
        messages.error(request, 'Фотография должна быть в формате [photo/video file_id]')
        n = False
    try:
        age = int(age)
        find_age = f'{age - 3}-{age + 3}'
        if age < 16 or age > 100:
            raise Exception
    except Exception:
        n = False
        messages.error(request, 'Возраст должен быть числом, больше 16 и меньше 100')
    city, latitude, longitude = get_coord_by_name(city)
    if not city:
        messages.error(request, 'Город не найден')
        n = False
    if n:
        user, _ = User.objects.get_or_create(
            chat_id=str(random.randint(1, 100000)),
            name=name,
            age=age,
            city=city,
            gender=gender,
            category=category,
            description=description,
            find_age=find_age,
            find_gender=seeking,
            longitude=longitude,
            latitude=latitude,
        )
        create_logs(request.user, f'Создание нового аккаунта')
        if photo1:
            photo1 = Photo.objects.create(
                file_id=photo1
            )
            user.avatars.add(photo1)
        elif photo2:
            photo3 = Photo.objects.create(
                file_id=photo3
            )
            user.avatars.add(photo3)
        elif photo3:
            photo3 = Photo.objects.create(
                file_id=photo3
            )
            user.avatars.add(photo3)
        return True
    else:
        return False


def create_ancete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif not request.user.groups.filter(name='создание аккаунтов'):
        return HttpResponseRedirect('/profiles')
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        seeking = request.POST.get('seeking')
        age = request.POST.get('age')
        city = request.POST.get('city')
        category = request.POST.get('category')
        description = request.POST.get('description')
        photo1 = request.POST.get('photo1')
        photo2 = request.POST.get('photo2')
        photo3 = request.POST.get('photo3')
        n = create_account(request=request, name=name, gender=gender, seeking=seeking, age=age, city=city,
                           category=category,
                           description=description, photo1=photo1, photo2=photo2, photo3=photo3)
        if n:
            return HttpResponseRedirect('/profiles')
        else:
            return render(request, 'create_ancete.html')
    else:
        return render(request, 'create_ancete.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/profiles')
        else:
            messages.error(request, 'Неверные имя пользователя или пароль.')
    return render(request, 'login.html')
