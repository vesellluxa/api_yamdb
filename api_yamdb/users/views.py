from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from users.serializers import UserSerializer, AdminSerializer, ConfirmCodeSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import YamDBUser
from users.permissions import IsAdmin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import LimitOffsetPagination


@permission_classes((AllowAny,))
@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(is_active=True)
    data = {
        "username": serializer.data.get('username'),
        "email": serializer.data.get('email')
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def obtain_token_view(request):
    serializer = ConfirmCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    user = get_object_or_404(YamDBUser, username=username)
    token = serializer.validated_data.get('confirmation_code')
    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        token = RefreshToken.for_user(user)
        access_token = {
            "token": str(token.access_token)
        }
        return Response(access_token, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.mixins.CreateModelMixin,
                  viewsets.mixins.DestroyModelMixin,
                  viewsets.mixins.UpdateModelMixin,
                  viewsets.mixins.RetrieveModelMixin,
                  viewsets.mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = YamDBUser.objects.all()
    permission_classes = (IsAdmin, IsAuthenticated)
    pagination_class = LimitOffsetPagination
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.user.role == 'admin':
            return AdminSerializer
        return UserSerializer

    @action(methods=['GET', 'PATCH'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(partial=True, role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
