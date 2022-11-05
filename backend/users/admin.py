from django.contrib import admin

from .models import User


@admin.register(User) 
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email')
    search_fields = ('username', 'email')
    list_filter = ('first_name',)
    empty_value_display = '-пусто-'
