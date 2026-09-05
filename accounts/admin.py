from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone_number')
    list_filter = ('created_at',)
