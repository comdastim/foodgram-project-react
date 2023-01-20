from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     Shopping_cart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug',)
    empty_value_display = '-пусто-'


admin.site.register(Favorite)

admin.site.register(Shopping_cart)


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
    list_display = ('id', 'name', 'author', 'favorite')
    readonly_fields = ('favorite',)
    search_fields = ('name', 'author', 'tag')
    list_filter = ('name',)
    inlines = [RecipeIngredientInline, RecipeTagInline]
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def favorite(self, obj):
        return obj.favorite_recipe.count()
