from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField('Тэг', max_length=200, unique=True)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=200)
    measurement_unit = models.CharField('Единицы измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField('Название рецепта', max_length=200)
    image = models.ImageField('Картинка',
                              upload_to='recipes/',
                              blank=True)
    text = models.TextField('Текст рецепта',
                            help_text='Введите текст рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient', through='RecipeIngredient')
    tags = models.ManyToManyField('Tag', through='RecipeTag')
    cooking_time = models.IntegerField('Время приготовления')

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_amount')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients_amount')
    amount = models.IntegerField('Количество')

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.recipe}{self.ingredient}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe}{self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorite')

    class Meta:
        verbose_name = 'Понравившийся рецепт'
        verbose_name_plural = 'Понравившиеся рецепты'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Shopping_cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='shopping_cart')

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower', verbose_name='Подписчик')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following', verbose_name='Автор'
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')]

    def _str_(self):
        return f'{self.user}{self.following}'
