from django.contrib import admin

from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, Shopping_cart, Tag



class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug') 
    search_fields = ('name', 'color', 'slug') 
    list_filter = ('name', 'color', 'slug',) 
    empty_value_display = '-пусто-'  

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit') 
    search_fields = ('name') 
    list_filter = ('name', ) 
    empty_value_display = '-пусто-'  

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author') 
    search_fields = ('author','tag','ingredient') 
    list_filter = ('name',) 
    empty_value_display = '-пусто-'  

class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe') 
    list_filter = ('user',) 
    empty_value_display = '-пусто-'  

class Shopping_cartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe') 
    list_filter = ('user',) 
    empty_value_display = '-пусто-'  

    
admin.site.register(Favorite) 
admin.site.register(Ingredient) 
admin.site.register(Recipe) 
admin.site.register(Shopping_cart) 
admin.site.register(Tag) 
