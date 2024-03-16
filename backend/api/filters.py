from django_filters import FilterSet, filters
from recipes.models import (
    Recipe,
    Ingredient,
)


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    author = filters.NumberFilter(
        field_name='author_id')
    tags = filters.CharFilter(
        method='filter_by_tags')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if user.is_authenticated:
            if self.request.query_params.get('is_favorited'):
                queryset = queryset.filter(favorite__user=user)
            if self.request.query_params.get('is_in_shopping_cart'):
                queryset = queryset.filter(shoppinglist__user=user)
        return queryset

    def filter_by_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__slug__in=tags)
