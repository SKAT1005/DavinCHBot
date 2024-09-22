from django.contrib import admin
from .models import User, Status


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass
