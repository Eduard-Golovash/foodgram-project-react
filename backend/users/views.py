from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from api.paginations import Paginator
from api.serializers import (
    UserSerializer,
    UserCreateSerializer,
    SetPasswordSerializer,
    SubscriptionSerializer,
    SubscriptionActionSerializer
)
from users.models import User, Subscription


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    pagination_class = Paginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user,
                                    context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        if not user.check_password(current_password):
            return Response({'error': 'Неверный текущий пароль'},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({'detail': 'Пароль успешно обновлен'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=Paginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscription_author__user=request.user)
        for user in queryset:
            user.is_subscribed = True
        serializer = SubscriptionSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    # @action(detail=True, methods=['post'],
    #         permission_classes=(IsAuthenticated,))
    # def subscribe(self, request, **kwargs):
    #     author = get_object_or_404(User, id=kwargs['pk'])
    #     serializer = SubscriptionActionSerializer(
    #         data={'author': author}, context={'request': request})
    #     serializer.is_valid(raise_exception=True)
    #     subscription, created = Subscription.objects.get_or_create(
    #         user=request.user, author=author)
    #     if not created:
    #         return Response(
    #             {'error': 'Вы уже подписаны на этого пользователя'},
    #             status=status.HTTP_400_BAD_REQUEST)
    #     return Response(
    #         {'message': 'Подписка успешно создана'},
    #         status=status.HTTP_201_CREATED
    #     )

    # @subscribe.mapping.delete
    # def delete_subscribe(self, request, **kwargs):
    #     author = get_object_or_404(User, id=kwargs['pk'])
    #     subscription = Subscription.objects.filter(
    #         user=request.user, author=author).first()
    #     if not subscription:
    #         return Response({'errors': 'Подписка не существует'},
    #                         status=status.HTTP_400_BAD_REQUEST)
    #     subscription.delete()
    #     serializer = SubscriptionActionSerializer(
    #         author, context={'request': request})
    #     data = serializer.data
    #     data['is_subscribed'] = False
    #     return Response(data, status=status.HTTP_204_NO_CONTENT)
    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        subscription, created = Subscription.objects.get_or_create(
            user=request.user, author=author)
        if not created:
            return Response(
                {'error': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = SubscriptionActionSerializer(
            author, context={'request': request})
        data = serializer.data
        data['is_subscribed'] = True
        return Response(data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        subscription = Subscription.objects.filter(
            user=request.user, author=author).first()
        if not subscription:
            return Response({'errors': 'Подписка не существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        serializer = SubscriptionActionSerializer(
            author, context={'request': request})
        data = serializer.data
        data['is_subscribed'] = False
        return Response(data, status=status.HTTP_204_NO_CONTENT)
