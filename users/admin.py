from django.contrib import admin
from .models import User, Report, Logs


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Logs)
class LogsAdmin(admin.ModelAdmin):
    fields = ('time', 'type', 'user')
    list_display = ('id', 'user', 'type', 'time')
    list_filter = ('user', )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass
