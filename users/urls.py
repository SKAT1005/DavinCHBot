from django.urls import path

from .views import user_view, delete_profile, ban_profile, EditProfile, stat, verefi, acept_verefi, cansel_verefi, \
    cansel_report, report, ad_list, create_ad, delete_ad, deactivate_ad, create_ancete, login_view

urlpatterns = [
    path('', login_view, name='login'),
    path("profiles", user_view, name="user_list"),
    path("profiles/delete/<int:pk>", delete_profile, name="delete_profile"),
    path("profiles/ban/<int:pk>", ban_profile, name="ban_profile"),
    path("profiles/edit/<int:pk>", EditProfile.as_view(), name="edit_profile"),
    path('profiles/create', create_ancete, name="create_ancete"),
    path('stat', stat, name="stat"),
    path('verefi', verefi, name="verefi"),
    path('verefi/acept/<int:pk>', acept_verefi, name="acept_verefi"),
    path('verefi/cansel/<int:pk>', cansel_verefi, name="cansel_verefi"),
    path('reports', report, name="report"),
    path('reports/cansel/<int:pk>', cansel_report, name="cansel_report"),
    path('ad', ad_list, name="ad_list"),
    path('ad/create', create_ad, name="create_ad"),
    path('ad/delete/<int:pk>', delete_ad, name="delete_ad"),
    path('ad/deactivate/<int:pk>', deactivate_ad, name="deactivate_ad"),

]
