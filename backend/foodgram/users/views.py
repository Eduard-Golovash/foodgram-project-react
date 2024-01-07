from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated

from users.models import User
from api.serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    CustomSetPasswordSerializer
)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        return CustomUserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = CustomSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        if not user.check_password(current_password):
            return Response({'error': 'Неверный текущий пароль'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({'detail': 'Пароль успешно обновлен'}, status=status.HTTP_204_NO_CONTENT)