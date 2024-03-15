from django_filters import FilterSet, filters
from recipes.models import Recipe, Ingredient


class IngredientFilter(FilterSet):
    class Meta:
        model = Ingredient
        fields = ['name']

    name = filters.CharFilter(lookup_expr='icontains')


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='favorites__user', method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shopping_lists__user', method='filter_is_in_shopping_cart')
    author = filters.CharFilter(field_name='author')
    tags = filters.CharFilter(field_name='tags__slug', method='filter_tags')

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_lists__user=self.request.user)
        return queryset

    def filter_tags(self, queryset, name, value):
        tags = value.split(',')
        return queryset.filter(tags__slug__in=tags)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
