import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Shopping_cart, Subscription, Tag

from users.models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    id = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user != obj and Subscription.objects.filter(
            user=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True},
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя использовать "me" в никнейме.'
            )
        return value


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientAddSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time')

    def recipe_ingredient_create(self, recipe, ingredients):
        recipe_list = [RecipeIngredient(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        ) for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_list)

    def to_representation(self, value):
        return RecipeListSerializer(value, context=self.context).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.recipe_ingredient_create(
            recipe=recipe,
            ingredients=ingredients
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if "tags" in validated_data:
            tags = validated_data.pop('tags')
            instance.tags.clear()
            instance.tags.set(tags)
        if "ingredients" in validated_data:
            ingredients = validated_data.pop('ingredients')
            RecipeIngredient.objects.filter(recipe=instance).delete()
            instance.ingredients.clear()
            self.recipe_ingredient_create(
                recipe=instance,
                ingredients=ingredients
            )
        return super().update(instance, validated_data)

    def to_representation(self, value):
        return RecipeListSerializer(value, context=self.context).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Favorite.objects.filter(
               user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Shopping_cart.objects.filter(
            user=request.user, recipe=obj).exists())


# сериализаторы для чтения рецепта

class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image',
                  'text', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart', 'ingredients', 'tags')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Favorite.objects.filter(
               user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Shopping_cart.objects.filter(
            user=request.user, recipe=obj).exists())


class Favorite_Shopping_cartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionListSerializer(CustomUserSerializer):

    recipes = RecipeSubscriptionSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
