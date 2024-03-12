from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenDestroyView

from users.views import UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/token/logout/',
         TokenDestroyView.as_view(), name='token_destroy'),
]
