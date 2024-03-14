from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientsViewSet,
    TagsViewSet,
    RecipesViewSet
)


router = DefaultRouter()
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('api/recipes/download_shopping_cart/',
         RecipesViewSet.as_view({'get': 'download_shopping_cart'}),
         name='download_shopping_cart'),
]
