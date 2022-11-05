from api.serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                             FavoriteSerializer, IngredientSerializer,
                             RecipeListSerializer, RecipeSerializer,
                             Shopping_cartSerializer,
                             SubscriptionDetailSerializer,
                             SubscriptionListSerializer, TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            Shopping_cart, Tag)
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User

from .permissions import IsAuthorOrReadOnlyPermission


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    # pagination_class = LimitOffsetPagination
    permission_classes = (IsAuthorOrReadOnlyPermission,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def change_favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        added = Favorite.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if added.exists():
                return Response(
                    {'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite, data=request.data)
            serializer.save()
            return Response(
                {'Рецепт успешно добавлен в избранное'},
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if added. exists():
                added.delete()
                return Response(
                    {'Рецепт успешно удален из избранного'},
                    status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'Рецепт отсутствует в избранном'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def change_shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        added = Shopping_cart.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if added.exists():
                return Response({'Рецепт уже добавлен в список покупок'},
                                status=status.HTTP_400_BAD_REQUEST)

            shopping_cart = Shopping_cart.objects.create(
                user=user, recipe=recipe)
            serializer = Shopping_cartSerializer(
                shopping_cart, data=request.data)
            serializer.save()
            return Response({'Рецепт успешно добавлен в список покупок'},
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if added. exists():
                added.delete()
                return Response({'Рецепт успешно удален из списка покупок'},
                                status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепт отсутствует в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)

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


class SubscribeDetail(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionDetailSerializer

    def delete(self, request, pk):
        user = request.user
        following = get_object_or_404(User, id=pk)
        follow_to_delete = Subscription.objects.filter(
            user=user, following=following)
        if follow_to_delete.exists():
            follow_to_delete.delete()
            return Response({'Подписка отменена'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'Подписка не существует'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscribeList(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionListSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(
        detail=True,
        methods=['post', 'delete']
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = kwargs.get('id')
        author = get_object_or_404(user, id=author_id)
        subscription = Subscription.objects.filter(
            user=user,
            author=author
        )
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'Нельзя подписываться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscription.exists():
                return Response(
                    {'Подписка уже оформлена'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionListSerializer(
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
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get']
    )
    def get_subscriptions(self, request):
        queryset = User.objects.filter(
            author__user=request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionListSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionListSerializer(
            queryset, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
