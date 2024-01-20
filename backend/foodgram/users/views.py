from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from users.models import User, Subscription
from api.serializers import (
    CustomUserSerializer,
    CustomUserCreateSerializer,
    CustomSetPasswordSerializer,
    SubscriptionSerializer,
    SubscriptionActionSerializer
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
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'], permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(request.user, context={'request': request})
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

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),)
            # pagination_class=CustomPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscription_author__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        if request.method == 'POST':
            if request.user == author:
                return Response({'error': 'Вы не можете подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            subscription, created = Subscription.objects.get_or_create(user=request.user, author=author)
            if not created:
                return Response({'error': 'Вы уже подписаны на этого пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            subscription = get_object_or_404(Subscription, user=request.user, author=author)
            subscription.delete()
        serializer = SubscriptionActionSerializer(author, context={'request': request})
        data = serializer.data
        data['is_subscribed'] = request.method == 'POST'
        return Response(data, status=status.HTTP_201_CREATED if request.method == 'POST' else status.HTTP_204_NO_CONTENT)