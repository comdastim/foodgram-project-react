# Дописать Meta и def _str_self

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField('Тэг', max_length=200, unique=True)
    color = models.CharField('Цветовой HEX-код', max_length=20, unique=True)
    slug = models.SlugField(max_length=200, unique=True)


class Ingredient(models.Model):
    name = models.CharField('Название',max_length=200)
    measurement_unit = models.CharField('Единицы измерения', max_length=200)


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes') 
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Картинка',
  #      upload_to='recipes/',
        blank=True
    )
    text= models.TextField('Текст рецепта',
                            help_text='Введите текст рецепта')    
    ingredients = models.ManyToManyField('Ingredient', through = 'RecipeIngredient')
    tags = models.ManyToManyField('Tag')
    cooking_time = models.TimeField('Время приготовления')


    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:15]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField ('Количество')




class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )


class Favorite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'favorite')
    recipe = models.ManyToManyField('Recipe', related_name = 'favorite')


class Shopping_cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'shopping_cart')
    recipe = models.ManyToManyField('Recipe', related_name = 'shopping_cart')
