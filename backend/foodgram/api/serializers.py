from rest_framework import serializers
from djoser.serializers import UserSerializer, UserCreateSerializer

from users.models import User

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')


class CustomUserCreateSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'password', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request_user = self.context['request'].user
        return request_user.subscribers.filter(id=obj.id).exists()


class CustomSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)
