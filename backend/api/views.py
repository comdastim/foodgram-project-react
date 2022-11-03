from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Shopping_cart, Tag
from rest_framework import filters, permissions, status, viewsets 
from api.serializers import IngredientSerializer, TagSerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = [AllowAny]
    # pagination_class = None

class IngredientViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = Ingredient.objects.all() 
    serializer_class = IngredientSerializer 
   # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
   # pagination_class = None