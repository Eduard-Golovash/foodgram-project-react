from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Subscription


class UserAdmin(UserAdmin):
    list_filter = UserAdmin.list_filter + ('email', 'username')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
