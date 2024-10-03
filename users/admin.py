from django.contrib import admin
from .models import User, Status, LikeUsers, Report


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass



@admin.register(LikeUsers)
class LikeUsersAdmin(admin.ModelAdmin):
    pass


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass
