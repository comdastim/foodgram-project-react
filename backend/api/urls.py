from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')

favorite = RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'})
shopping_cart = RecipeViewSet.as_view({'post': 'shopping_cart',
                                       'delete': 'shopping_cart',
                                       'get': 'shopping_cart'})
subscriptions = CustomUserViewSet.as_view({'post': 'subscriptions',
                                           'delete': 'subscriptions',
                                           'get': 'subscriptions'})

urlpatterns = (
    path('<int:user_id>/subscribe/',
         CustomUserViewSet.as_view, name='subscribe'),
    path('subscriptions/', CustomUserViewSet.as_view, name='subscriptions'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
