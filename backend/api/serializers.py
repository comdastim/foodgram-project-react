from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag, Shopping_cart, Tag
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from users.models import User

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
    id= serializers.ReadOnlyField(source='ingredient.id')
    name= serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit= serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit','amount')

class IngredientAddSerializer(serializers.ModelSerializer):
    id=serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount=serializers.IntegerField(min_value=1)

    class Meta:
        model=RecipeIngredient
        fields=('id','amount')


class RecipeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    image=Base64ImageField(required=True)
    text= serializers.CharField(required=True)
    ingredients = IngredientAddSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    # tags=serializers.PrimaryKeyRelatedField(queryset-Tag.objects.all())
    cooking_time=serializers.IntegerField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time')

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
    # author= serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientAddSerializer(read_only=True)
    # ingredients = serializers.SerializerMethodField(read_only=True)
    is_in_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time', 'is_in_favorited', 'is_in_shopping_cart')

    def get_ingredients(self,obj):
        ingredients=RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_in_shopping_cart(self,obj):
        request=self.context.get('request')
        if request.user.is_authenticated:
            return Shopping_cart.objects.filter(user=request.user,
            recipe=obj).exists
    
    def get_is_in_favorite(self,obj):
        request=self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
            recipe=obj).exists

class FavoriteSerializer(serializers.ModelSerializer):
    user=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe=serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

class Shopping_cartSerializer(serializers.ModelSerializer):
    user=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe=serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    
    class Meta:
        model = Shopping_cart
        fields = ('user', 'recipe')
