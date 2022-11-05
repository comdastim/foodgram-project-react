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

subscriptions = CustomUserViewSet.as_view({'get': 'subscriptions', })

urlpatterns = (
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    # path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
)
