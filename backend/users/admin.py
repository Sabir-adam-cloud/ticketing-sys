from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplementaires', {'fields': ('phone', 'address', 'role')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplementaires', {'fields': ('email', 'phone', 'address', 'role')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = UserAdmin.list_filter + ('role',)
