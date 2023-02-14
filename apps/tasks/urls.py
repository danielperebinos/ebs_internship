from django.urls import path
from apps.tasks import views


urlpatterns = [
    path("create", views.CreateTaskView.as_view(), name="create_task"),
    path("all", views.ListTaskView.as_view(), name="all_tasks"),
    path("get/<pk>", views.TaskView.as_view(), name="get_task"),
    path("my_tasks", views.ListTaskByUserView.as_view(), name="my_tasks"),
    path("completed", views.ListCompletedTaskView.as_view(), name="completed_tasks"),
    path("assign/<pk>", views.UpdateTaskUserView.as_view(), name="assign_tasks"),
    path("update_status/<pk>", views.UpdateTaskStatusView.as_view(), name="update_status"),
    path("complete/<pk>", views.CompleteTaskView.as_view(), name="complete"),
    path("delete/<pk>", views.DeleteTaskView.as_view(), name="delete"),
]
