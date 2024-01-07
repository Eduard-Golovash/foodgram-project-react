from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenDestroyView

from users.views import CustomUserViewSet
from recipes.views import (
    IngredientsViewSet,
    TagsViewSet,
    RecipesViewSet
)


router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipe')
# router.register(r'favorites', FavoritesViewSet, basename='favorites')



urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='token_destroy'),
    # path('api/recipes/<int:recipe_id>/shopping_cart/',
    #      ShoppingCartViewSet.as_view({
    #          'post': 'shopping_cart', 'delete': 'shopping_cart'}),
    #      name='recipe_shopping_cart'),
    # path('api/recipes/download_shopping_cart/',
    #      DownloadShoppingCartViewSet.as_view({'get': 'download_shopping_cart'}),
    #      name='download_shopping_cart'),
]