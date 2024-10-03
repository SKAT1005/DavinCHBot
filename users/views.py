from django.db.models import Q
from django.shortcuts import render

from buttons import questionnaire_menu
from users.models import User


def user_view(request):
    if request.method == 'GET':
        filter = Q()
        sorting = request.GET.get('sorting')
        age = request.GET.get('age')
        try:
            if age:
                filter &= Q(age__range=list(map(int, age.split('-'))))
        except Exception:
            pass
        gender = request.GET.get('gender')
        if gender:
            filter &= Q(gender=gender)
        city = request.GET.get('city')
        if city:
            filter &= Q(city=city)
        category = request.GET.get('category')
        if category:
            filter &= Q(category=category)
        description = request.GET.get('description')
        if description == 'нет':
            filter &= Q(description='🫢🤫')
        elif description == 'да':
            filter &= ~Q(description='🫢🤫')
        if filter:
            users = User.objects.filter(filter)
        else:
            users = User.objects.all()
        unique_cities = User.objects.values_list('city', flat=True).distinct()
        return render(request, 'user_list.html', {'users': users, 'citys': unique_cities})
