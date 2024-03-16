from django_filters import FilterSet, filters
from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingList
)


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            favorite_recipes = Favorite.objects.filter(
                user=user).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=favorite_recipes)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            shopping_list_recipes = ShoppingList.objects.filter(
                user=user).values_list('recipe_id', flat=True)
            return queryset.filter(id__in=shopping_list_recipes)
        return queryset
