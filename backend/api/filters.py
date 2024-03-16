from django_filters import FilterSet, filters
from recipes.models import Recipe, Ingredient, Tag


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

    # is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    # is_in_shopping_cart = filters.BooleanFilter(
    #     method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    # def filter_is_favorited(self, queryset, name, value):
    #     user = self.request.user
    #     if value and not user.is_anonymous:
    #         return queryset.filter(favorites__user=user)
    #     return queryset

    # def filter_is_in_shopping_cart(self, queryset, name, value):
    #     user = self.request.user
    #     if value and not user.is_anonymous:
    #         return queryset.filter(shopping_cart__user=user)
    #     return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.request and self.request.user.is_authenticated:
            if self.request.method == 'GET':
                if 'is_favorited' in self.request.query_params:
                    if self.request.query_params.get(
                        'is_favorited') == 'true':
                        queryset = queryset.filter(
                            favorites__user=self.request.user)
                if 'is_in_shopping_cart' in self.request.query_params:
                    if self.request.query_params.get(
                        'is_in_shopping_cart') == 'true':
                        queryset = queryset.filter(
                            shopping_cart__user=self.request.user)
        return queryset
