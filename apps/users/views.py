from django.contrib.auth.models import User
from drf_util.decorators import serialize_decorator
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.users.serializers import UserSerializer, UserReadSerializer


# Create your views here.


class RegisterUserView(GenericAPIView):
    serializer_class = UserSerializer

    permission_classes = (AllowAny,)
    authentication_classes = ()

    @serialize_decorator(UserSerializer)
    def post(self, request):
        validated_data = request.serializer.validated_data

        # Get password from validated data
        password = validated_data.pop("password")

        # Create user
        user = User.objects.create(**validated_data)

        # Set password
        user.set_password(password)
        user.save()

        return Response(UserSerializer(user).data)


class GetListUserView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserReadSerializer
