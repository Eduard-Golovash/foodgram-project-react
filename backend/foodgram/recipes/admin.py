from django.contrib import admin

from .models import (
    Recipe,
    Tag,
    Ingredient,
    Favorite,
    ShoppingList
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author_name', 'total_favorites')
    list_filter = ('author', 'name', 'tags')

    def author_name(self, obj):
        return obj.author.username

    def total_favorites(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    total_favorites.short_description = 'Total Favorites'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
