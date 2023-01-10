from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, Shopping_cart, Tag)
from rest_framework import serializers
from users.models import Subscription, User


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


class SubscriptionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Subscription

    def validate(self, data):
        user = self.context['request'].user
        follow = data['following']
        if user == follow:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя"
            )
        if Subscription.objects.filter(
                user=user,
                following=follow
        ).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого автора"
            )
        return data


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="following.id")
    username = serializers.ReadOnlyField(source="following.username")
    following = serializers.SerializerMethodField("get_following")
    recipes = serializers.SerializerMethodField('get_recipes')
    count_of_recipes = serializers.SerializerMethodField("get_recipes_count")

    class Meta:
        model = User
        fields = ('id', 'username', 'following', 'recipes', 'count_of_recipes')

    def get_following(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return Subscription.objects.filter(
                user=user, following=obj.id).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.following)
        serializer = RecipeSubscriptionSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.id).count()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__',


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


# class IngredientAddSerializer(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    # amount = serializers.IntegerField(min_value=1)

    # class Meta:
        # model = RecipeIngredient
        # fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    image = Base64ImageField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)
    ingredients = RecipeIngredientSerializer(source='recipeingredient_set', many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time')

    def recipe_ingredient_create(cls, recipe, ingredients):
        recipe_list = [RecipeIngredient(
            recipe=recipe,
            ingredients=get_object_or_404(Ingredient, id=ingredient['id']),
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
        ingredients = self.context['request'].data['ingredients']
        tags = self.context['request'].data['tags']
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        if tags:
            RecipeTag.objects.filter(recipe=instance).delete()
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            instance.ingredients.clear()
            self.recipe_ingredient_create(
                recipe=instance,
                ingredients=ingredients
            )
        return instance


class RecipeListSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    # tags = TagSerializer(many=True, read_only=True)
    # ingredients = IngredientSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Favorite.objects.filter(
               user=request.user, recipe=obj).exists)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Shopping_cart.objects.filter(
            user=request.user, recipe=obj).exists)


class Favorite_Shopping_cartSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = '__all__',
