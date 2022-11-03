from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Shopping_cart, Tag
from rest_framework import filters, permissions, status, viewsets 
from api.serializers import FavoriteSerializer, IngredientSerializer, RecipeListSerializer, RecipeSerializer, Shopping_cartSerializer,TagSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404 
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Sum

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


class RecipeViewSet(viewsets.ModelViewSet): 
    queryset = Recipe.objects.all() 
    serializer_class = RecipeSerializer 
    # permission_classes = (IsAuthorOrReadOnlyPermission,) 
    # pagination_class = LimitOffsetPagination 
 
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeListSerializer
        return RecipeSerializer


    @action (
        methods=['POST', 'DELETE'],
        detail=True,
        # permission_classes=[IsAuthenticated]
    )
    def change_favorite(self,request, pk):
        user=request.user
        recipe= get_object_or_404(Recipe, id=pk)
        added = Favorite.objects.filter(user=user, recipe=recipe) 
        if request.method == 'POST':
            if added.exists():
                return Response({'Рецепт уже добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            favorite=Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite, data=request.data)
            serializer.save()
            return Response({'Рецепт успешно добавлен в избранное'},
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if added. exists ():
                added.delete()
                return Response({'Рецепт успешно удален из избранного'},
                   status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепт отсутствует в избранном'},
                 status=status.HTTP_400_BAD_REQUEST)

    
    @action (
        methods=['POST', 'DELETE'],
        detail=True,
        # permission_classes=[IsAuthenticated]
    )
    def change_shopping_cart(self,request, pk):
        user=request.user
        recipe= get_object_or_404(Recipe, id=pk)
        added = Shopping_cart.objects.filter(user=user, recipe=recipe) 
        if request.method == 'POST':
            if added.exists():
                return Response({'Рецепт уже добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            shopping_cart=Shopping_cart.objects.create(user=user, recipe=recipe)
            serializer = Shopping_cartSerializer(shopping_cart, data=request.data)
            serializer.save()
            return Response({'Рецепт успешно добавлен в список покупок'},
                status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if added. exists ():
                added.delete()
                return Response({'Рецепт успешно удален из списка покупок'},
                   status=status.HTTP_204_NO_CONTENT)
            return Response({'Рецепт отсутствует в списке покупок'},
                 status=status.HTTP_400_BAD_REQUEST)
            
    @action (
        methods=['GET'],
        detail= False,
        # permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(amount=Sum('amount'))
        shopping_list = set_shopping_list(user.get_full_name(), ingredients)
        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

             