from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from api.filters import (
    IngredientFilter,
    RecipeFilter
)
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeListSerializer,
    RecipeCreateUpdateSerializer,
    RecipeIngredient,
    DownloadShoppingCartSerializer,
    FavoriteShoppingListSerializer
)
from api.paginations import Paginator
from api.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Ingredient,
    Tag,
    Recipe,
    ShoppingList,
    Favorite
)


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    pagination_class = Paginator
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,), pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        recipe = Recipe.objects.filter(pk=kwargs['pk']).first()
        if not recipe:
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = FavoriteShoppingListSerializer(
            recipe, context={'request': request})
        if not ShoppingList.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            ShoppingList.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже есть в списке покупок'},
                        status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        try:
            shopping_cart = ShoppingList.objects.get(
                user=request.user, recipe=recipe)
            shopping_cart.delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT)
        except ShoppingList.DoesNotExist:
            return Response(
                {'errors': 'Рецепт не найден в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        shopping_cart = ShoppingList.objects.filter(user=request.user)
        recipes = [item.recipe for item in shopping_cart]
        ingredients = (
            RecipeIngredient.objects.filter(recipe__in=recipes)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        serializer = DownloadShoppingCartSerializer(
            data=ingredients, many=True)
        serializer.is_valid()
        response = HttpResponse(content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        font_path = '/app/FreeSans.ttf'
        pdfmetrics.registerFont(TTFont('FreeSans', font_path))
        p = canvas.Canvas(response)
        p.setFont('FreeSans', 12)
        p.drawString(100, 750, "Список покупок:")
        y = 730
        for ingredient in serializer.data:
            y -= 15
            text = "{} - {} {}".format(
                ingredient['ingredient_name'],
                ingredient['total_amount'],
                ingredient['measurement_unit']
            ).encode('utf-8')
            p.drawString(100, y, text.decode('utf-8'))
        p.showPage()
        p.save()
        return response

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        recipe = Recipe.objects.filter(pk=kwargs['pk']).first()
        if not recipe:
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = FavoriteShoppingListSerializer(
            recipe, context={'request': request})
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'errors': 'Рецепт уже есть в избранном'},
                        status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        try:
            favorite = Favorite.objects.get(user=request.user, recipe=recipe)
            favorite.delete()
            return Response({'detail': 'Рецепт успешно удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({'errors': 'Рецепт не найден в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
