import os

import django

from const import bot
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DavinCHBot.settings')
django.setup()
import math

def is_point_in_circle(latitude, longitude, circle_center_latitude, circle_center_longitude, radius_km=5):

  # Преобразуем углы в радианы
  latitude = math.radians(latitude)
  longitude = math.radians(longitude)
  circle_center_latitude = math.radians(circle_center_latitude)
  circle_center_longitude = math.radians(circle_center_longitude)

  # Вычисляем расстояние между точкой и центром круга по формуле Гаверсинуса
  distance_km = 2 * 6371 * math.asin(math.sqrt(
      math.sin((circle_center_latitude - latitude) / 2)**2 +
      math.cos(circle_center_latitude) * math.cos(latitude) *
      math.sin((circle_center_longitude - longitude) / 2)**2
  ))

  # Сравниваем расстояние с радиусом
  return distance_km <= radius_km


def filter_users(chat_id, user):









def callback(data, chat_id, user):
    if len(data) == 0:
        pass