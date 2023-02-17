from django.urls import path, include
from rest_framework import routers

from apps.tasks import views

router = routers.SimpleRouter()
router.register(r'task', views.TaskViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'timer', views.TimerLogViewSet)

urlpatterns = []
urlpatterns += router.urls
