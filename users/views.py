from django.db.models import Q, Count
from django.shortcuts import render, HttpResponseRedirect
from django.views import View

from buttons import questionnaire_menu
from users.models import User, Report


def user_view(request):
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
    try:
        user = User.objects.get(id=pk)
        reports = Report.objects.filter(user=user)
        if reports:
            reports.delete()
        user.delete()
    except Exception:
        pass
    return HttpResponseRedirect('/profiles')


def ban_profile(request, pk):
    try:
        user = User.objects.get(id=pk)

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
        try:
            user = User.objects.get(id=pk)
            return render(request, 'edit_profile.html', context={'user': user})
        except Exception:
            return  HttpResponseRedirect('/profiles')

    def post(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            description = request.POST.get('description')
            user.description = description
            user.save(update_fields=['description'])
            return render(request, 'edit_profile.html', context={'user': user})
        except Exception:
            return HttpResponseRedirect('/profiles')


def stat(request):
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
    users = User.objects.filter(need_verefi=True)
    return render(request, 'verefi.html', context={'users': users})


def acept_verefi(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.is_checked = True
        user.need_verefi = False
        user.check_photo = None
        user.check_simbol = None
        user.save(update_fields=['is_checked', 'need_verefi', 'check_photo', 'check_simbol'])
    except Exception:
        pass
    return HttpResponseRedirect('/verefi')


def cansel_verefi(request, pk):
    try:
        user = User.objects.get(id=pk)
        user.is_checked = False
        user.need_verefi = False
        user.check_photo = None
        user.check_simbol = None
        user.save(update_fields=['is_checked', 'need_verefi', 'check_photo', 'check_simbol'])
    except Exception:
        pass
    return HttpResponseRedirect('/verefi')



def report(request):
    reports = Report.objects.all()
    return render(request, 'reports.html', context={'reports': reports})


def cansel_report(request, pk):
    try:
        Report.objects.get(id=pk).delete()
    except Exception:
        pass
    return HttpResponseRedirect('/reports')