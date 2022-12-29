from .models import (Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag)
from django.contrib import admin


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )
    empty_value_display = '-пусто-'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient

class RecipeTagInline(admin.TabularInline):
    model = RecipeTag

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author')
    search_fields = ('name','author', 'tag')
    list_filter = ('name',)
    inlines = [RecipeIngredientInline, RecipeTagInline]
    empty_value_display = '-пусто-'
