import openpyxl
from django.db.models import Count
from django.utils import timezone
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.label import DataLabelList

from .models import User, Links


def users_count(wb):
    ws = wb.active
    ws.title = 'Количество пользователей'
    users_count = User.objects.all().count()
    ws.append(['Общее количество пользователей', users_count])


def new_users(wb):
    ws = wb.create_sheet("Новые пользователи")
    users = User.objects.all()
    new_user_count = 0
    now = timezone.now()
    for user in users:
        if user.registration_date.day == now.day and user.registration_date.year == now.year and user.registration_date.month == now.month:
            new_user_count += 1
    data = [
        ['', 'Количество пользователей'],
        ['Новые', new_user_count],
        ['Старые', users.count()-new_user_count]
    ]
    for row in data:
        ws.append(row)

    pie1 = PieChart()
    labels = Reference(ws, min_col=1, min_row=2, max_row=3)
    data_values1 = Reference(ws, min_col=2, min_row=2, max_row=3)

    pie1.set_categories(labels)
    pie1.add_data(data_values1)

    pie1.title = "Соотношение новых и старых пользователей"

    pie1.dataLabels = DataLabelList()
    pie1.dataLabels.showPercent = True
    pie1.dataLabels.showVal = False
    pie1.dataLabels.showCatName = False
    pie1.dataLabels.showSerName = False

    ws.add_chart(pie1, "F1")


def geoposition(wb):
    ws = wb.create_sheet("Статистика по городам")
    data = [['Название города', 'Количество пользователей']]
    users_by_city = User.objects.values('city').annotate(user_count=Count('city')).order_by()
    for item in users_by_city:
        if item['city']:  # Исключаем пользователей, у которых не указан город
            data.append([item['city'], item['user_count']])
    for row in data:
        ws.append(row)

    pie1 = PieChart()
    labels = Reference(ws, min_col=1, min_row=2, max_row=len(data))
    data_values1 = Reference(ws, min_col=2, min_row=2, max_row=len(data))

    pie1.set_categories(labels)
    pie1.add_data(data_values1)

    pie1.title = "Статистика по городам"

    pie1.dataLabels = DataLabelList()
    pie1.dataLabels.showPercent = True
    pie1.dataLabels.showVal = False
    pie1.dataLabels.showCatName = False
    pie1.dataLabels.showSerName = False

    ws.add_chart(pie1, "F1")


def age(wb):
    ws = wb.create_sheet("Статистика по возрасту")
    data = [['Возраст', 'Количество пользователей']]
    users_by_city = User.objects.values('age').annotate(user_count=Count('age')).order_by()
    for item in users_by_city:
        if item['age']:  # Исключаем пользователей, у которых не указан город
            data.append([item['age'], item['user_count']])

    for row in data:
        ws.append(row)

    pie1 = PieChart()
    labels = Reference(ws, min_col=1, min_row=2, max_row=len(data))
    data_values1 = Reference(ws, min_col=2, min_row=2, max_row=len(data))

    pie1.set_categories(labels)
    pie1.add_data(data_values1)

    pie1.title = "Статистика по возрасту"

    pie1.dataLabels = DataLabelList()
    pie1.dataLabels.showPercent = True
    pie1.dataLabels.showVal = False
    pie1.dataLabels.showCatName = False
    pie1.dataLabels.showSerName = False

    ws.add_chart(pie1, "F1")


def match_count(wb):
    ws = wb.create_sheet("Статистика мэтчей")
    users = User.objects.all()
    match_count = 0
    for user in users:
        match_count += user.like_users.all().count()
    ws.append(['Общее количество мэтчей', match_count])


def gender(wb):
    ws = wb.create_sheet("Cоотношение полов")
    male_count = User.objects.filter(gender='мужской').count()
    female_count = User.objects.filter(gender='женский').count()
    data = [['', 'Количество'], ['Мужчины', male_count], ['Женщины', female_count]]
    for row in data:
        ws.append(row)
    pie1 = PieChart()
    labels = Reference(ws, min_col=1, min_row=2, max_row=3)
    data_values1 = Reference(ws, min_col=2, min_row=2, max_row=3)

    pie1.set_categories(labels)
    pie1.add_data(data_values1)

    pie1.title = "Половое соотношение пользователей"

    pie1.dataLabels = DataLabelList()
    pie1.dataLabels.showPercent = True
    pie1.dataLabels.showVal = False
    pie1.dataLabels.showCatName = False
    pie1.dataLabels.showSerName = False

    ws.add_chart(pie1, "F1")


def links(wb):
    ws = wb.create_sheet("Статистика ссылок")
    data = [['Название ссылки', 'Количество перешедших пользователей']]
    for link in Links.objects.all():
        data.append([link.name, link.user_count])
    for row in data:
        ws.append(row)


def statistics():
    wb = openpyxl.Workbook()
    users_count(wb)
    new_users(wb)
    geoposition(wb)
    age(wb)
    match_count(wb)
    gender(wb)
    links(wb)
    return wb
