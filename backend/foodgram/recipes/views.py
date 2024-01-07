from django.http import HttpResponse
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)
from reportlab.pdfgen import canvas

from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    ShoppingList,
    Favorite
)
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    RecipeIngredient,
    DownloadShoppingCartSerializer
)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # filterset_class =
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, context={'request': request})
            if not ShoppingList.objects.filter(user=request.user, recipe=recipe).exists():
                shopping_list = ShoppingList.objects.create(user=request.user, recipe=recipe)
                shopping_list.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже есть в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(ShoppingList, user=request.user, recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из списка покупок'})

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppinglist__user=request.user)
            .values('ingredient')
            .annotate(total_quantity=Sum('quantity'))
            .values_list('ingredient__name', 'total_quantity',
                         'ingredient__measurement_unit')
        )
        serializer = DownloadShoppingCartSerializer(data=ingredients, many=True)
        serializer.is_valid()
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        p = canvas.Canvas(response)
        p.drawString(100, 100, "Список покупок:")
        y = 80
        for ingredient in serializer.data:
            y -= 15
            p.drawString(100, y, "{} - {} {}".format(
                ingredient['ingredient_name'],
                ingredient['total_quantity'],
                ingredient['measurement_unit']))
        p.showPage()
        p.save()
        return response

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = self.get_object()

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, context={'request': request})
            if not Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже есть в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(Favorite, user=request.user, recipe=recipe).delete()
            return Response({'detail': 'Рецепт успешно удален из избранного'})