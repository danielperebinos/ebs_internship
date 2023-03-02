from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import RegisterUserView, GetListUserView

urlpatterns = [
    path("register", RegisterUserView.as_view(), name="token_register"),
    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("users", GetListUserView.as_view(), name="get_users"),
]
