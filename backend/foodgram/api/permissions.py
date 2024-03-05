from rest_framework.permissions import SAFE_METHODS, BasePermission
from recipes.models import Favorite
from users.models import Subscription


class IsAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
        ) or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        is_author = obj.author == request.user
        is_favorited_permission = (
            request.method == 'POST'
            and not Favorite.objects.filter(
                user=request.user, recipe=obj).exists()
        )
        is_subscribed_permission = (
            request.method == 'POST'
            and view.action == 'subscribe'
            and not Subscription.objects.filter(
                user=request.user, author=obj.author).exists()
        )
        return (
            is_author or is_favorited_permission or
            is_subscribed_permission or request.method in SAFE_METHODS
        )
