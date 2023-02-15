from django.urls import path, include
from apps.tasks import views


urlpatterns = [
    path("create_task", views.CreateTaskView.as_view(), name="create_task"),
    path("all_tasks", views.ListTaskView.as_view(), name="all_tasks"),
    path("get/<pk>", views.TaskView.as_view(), name="get_task"),
    path("my_tasks", views.ListTaskByUserView.as_view(), name="my_tasks"),
    path("completed_tasks", views.ListCompletedTaskView.as_view(), name="completed_tasks"),
    path("assign_task/", views.UpdateTaskUserView.as_view(), name="assign_tasks"),
    path("update_status/<pk>", views.UpdateTaskStatusView.as_view(), name="update_status"),
    path("complete_task/<pk>", views.CompleteTaskView.as_view(), name="complete"),
    path("delete_task/<pk>", views.DeleteTaskView.as_view(), name="delete"),

    path("comments/create", views.CreateCommentView.as_view(), name="create_comment"),
    path("comments/<pk>", views.TaskCommentsView.as_view(), name="create_comment"),
    path("search", views.SearchTaskView.as_view(), name="search_task"),

]
