from django.urls import path, include
from rest_framework import routers
from rest_framework_mongoengine import routers as mongo_routers

from apps.tasks import views

router = routers.SimpleRouter()
router.register(r'task', views.TaskViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'timer', views.TimeLogViewSet)

mongo_router = mongo_routers.SimpleRouter()
mongo_router.register(r'goals', views.GoalViewSet)

urlpatterns = [
    path(r"anonim/", views.AnonimView.as_view(), name='anonim'),
    path(r"countries", views.CountryDictView.as_view(), name='countries')
]

urlpatterns += router.urls
urlpatterns += mongo_router.urls
