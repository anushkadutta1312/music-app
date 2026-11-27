from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'display_name', 'created_at')
    search_fields = ('user__username', 'display_name')
    list_filter = ('role',)
