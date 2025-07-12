from django.contrib import admin
from .models import Account
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'phone', 'date_joined', 'last_login','is_admin', 'is_staff', 'is_active', 'is_superadmin')
    list_display_links = ('email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    ordering = ('-date_joined',)
    search_fields = ('email', 'username')
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(Account, AccountAdmin)
