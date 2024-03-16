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
    ShoppingListRecipeSerializer,
    FavoriteRecipeSerializer,
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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            if self.request.query_params.get('is_favorited'):
                queryset = queryset.filter(
                    favorite__user=self.request.user)
            if self.request.query_params.get('is_in_shopping_cart'):
                queryset = queryset.filter(
                    shoppinglist__user=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @staticmethod
    def add_to_list(model, serializer_class, user, pk, request):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'Рецепт уже в списке!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = serializer_class(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def remove_from_list(model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален из списка!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,), pagination_class=None)
    def shopping_cart(self, request, **kwargs):
        return self.add_to_list(
            ShoppingList,
            ShoppingListRecipeSerializer,
            request.user,
            kwargs['pk'],
            request
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, **kwargs):
        return self.remove_from_list(
            ShoppingList,
            request.user,
            kwargs['pk']
        )

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        return self.add_to_list(
            Favorite,
            FavoriteRecipeSerializer,
            request.user,
            kwargs['pk'],
            request
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, **kwargs):
        return self.remove_from_list(
            Favorite,
            request.user,
            kwargs['pk']
        )

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
