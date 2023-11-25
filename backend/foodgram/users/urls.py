from django.urls import path

from users.views import (
    UserListView,
    UserProfileView,
    CurrentUserView)

urlpatterns = [
	
    # path('api/users/', UserListView.as_view(), name='user-list'),
    # path('api/users/<int:id>/', UserProfileView.as_view(), name='user-profile'),
    # path('api/users/me/', CurrentUserView.as_view(), name='current-user')
]
