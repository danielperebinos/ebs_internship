from django.urls import path

from apps.tasks.views import CreateTaskView, ListTaskView, TaskView

urlpatterns = [
    path("create", CreateTaskView.as_view(), name="create_task"),
    path("all", ListTaskView.as_view(), name="all_tasks"),
    path("get/<pk>", TaskView.as_view(), name="get_task"),
]
