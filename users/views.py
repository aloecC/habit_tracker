from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.permisions import IsModerator
from users.serializers import (RegisterSerializer, UserSerializer,
                               UserSerializerForAnother)


class UserViewSet(viewsets.ModelViewSet):
    """Виев-сет для пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsModerator]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserSerializerForAnother
        return super().list(self, request, *args, **kwargs)


class RegisterView(viewsets.ViewSet):
    """Регистрация пользователя"""

    permission_classes = [AllowAny]

    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"user": UserSerializer(user).data}, status=201)
        return Response(serializer.errors, status=400)


class TokenObtainPairView(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
