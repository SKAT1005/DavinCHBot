from django.urls import path

from .views import user_view, delete_profile, ban_profile, EditProfile, stat, verefi, acept_verefi, cansel_verefi, cansel_report, report

urlpatterns = [
    path("profiles", user_view, name="user_list"),
    path("profiles/delete/<int:pk>", delete_profile, name="delete_profile"),
    path("profiles/ban/<int:pk>", ban_profile, name="ban_profile"),
    path("profiles/edit/<int:pk>", EditProfile.as_view(), name="edit_profile"),
    path('stat', stat, name="stat"),
    path('verefi', verefi, name="verefi"),
    path('verefi/acept/<int:pk>', acept_verefi, name="acept_verefi"),
    path('verefi/cansel/<int:pk>', cansel_verefi, name="cansel_verefi"),
    path('reports', report, name="report"),
    path('reports/cansel/<int:pk>', cansel_report, name="cansel_report"),
]
