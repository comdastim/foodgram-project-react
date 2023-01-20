from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                             Favorite_Shopping_cartSerializer,
                             IngredientSerializer, TagSerializer,
                             RecipeListSerializer, RecipeSerializer,
                             SubscriptionGetSerializer,
                             SubscriptionCreateSerializer,)
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            Shopping_cart,
                            Subscription,
                            Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(User, id=author_id)
        subscription = Subscription.objects.filter(
            user=user,
            author=author
        )
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'Подписываться на самого себя нельзя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscription.exists():
                return Response(
                    {'Подписка уже оформлена'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionCreateSerializer(
                author,
                context={'request': request},
            )
            Subscription.objects.create(
                user=user, author=author
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'Вы не подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        # url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user
        authors = Subscription.objects.filter(user=user)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionGetSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionGetSerializer(
            authors, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeSerializer

    @staticmethod
    def change_favorite_or_shopping_cart(model, recipe, request):
        object = model.objects.filter(
            user=request.user, recipe=recipe)
        if request.method == 'POST':
            if object.exists():
                return Response({'errors': 'Объект был добавлен ранее'},
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=request.user, recipe=recipe)
            serializer = Favorite_Shopping_cartSerializer(recipe)
            return Response(serializer.data, status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response({'Объект успешно удален'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'Объект не существует'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite'
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.change_favorite_or_shopping_cart(
            Favorite, recipe=recipe, request=request)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.change_favorite_or_shopping_cart(
            Shopping_cart, recipe=recipe, request=request)

    @action(
        methods=['GET'],
        detail=False,
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    amount=Sum('amount'))
        shopping_list = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
