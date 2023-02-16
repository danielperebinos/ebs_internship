from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.tasks import serializers
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from apps.tasks.models import Task, User

from django.core.mail import send_mail


class CreateTaskView(generics.GenericAPIView):
    serializer_class = serializers.CreateTaskSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = serializers.CreateTaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message": "Task assigned successfully"})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class ListTaskView(generics.ListAPIView):
    serializer_class = serializers.ListTaskSerializer
    queryset = Task.objects.all()


class TaskView(generics.RetrieveAPIView):
    serializer_class = serializers.ViewTaskSerializer
    queryset = Task.objects.all()


class ListTaskByUserView(generics.ListAPIView):
    serializer_class = serializers.ListTaskSerializer

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(user=user)


class ListCompletedTaskView(generics.ListAPIView):
    serializer_class = serializers.ListTaskSerializer

    def get_queryset(self):
        return Task.objects.filter(status_field='Done')


class UpdateTaskUserView(generics.UpdateAPIView):
    serializer_class = serializers.UpdateUserTaskSerializer
    queryset = Task.objects.all()

    def update(self, request, *args, **kwargs):
        instance = Task.objects.filter(id=request.data.get('task_id')).first()
        email = request.user.email
        serializer = self.get_serializer(instance=instance, data={'user': request.data.get('user_id')}, partial=True)

        if serializer.is_valid():
            serializer.save(start_at=datetime.now() if request.data.get('status_field') == 'In Process' else None)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)

    swagger_user_id = openapi.Parameter('user_id', openapi.IN_QUERY,
                                        description='The id of the user you want to assign task',
                                        type=openapi.TYPE_INTEGER)
    swagger_task_id = openapi.Parameter('task_id', openapi.IN_QUERY,
                                        description='The id of the task you want to assign',
                                        type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[swagger_user_id, swagger_task_id], request_body=no_body)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(manual_parameters=[swagger_user_id, swagger_task_id], request_body=no_body)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UpdateTaskStatusView(generics.UpdateAPIView):
    serializer_class = serializers.UpdateStatusTaskSerializer
    queryset = Task.objects.all()
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)


class CompleteTaskView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.UpdateStatusTaskSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data={'status_field': 'Done'}, partial=True)

        if serializer.is_valid():
            serializer.save()

        return Response(serializer.data)

    swagger_id_parameter = openapi.Parameter('id', openapi.IN_PATH, description='Task id', type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(request_body=no_body)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(request_body=no_body)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)


class DeleteTaskView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.UpdateStatusTaskSerializer
    lookup_field = 'pk'


class CreateCommentView(generics.GenericAPIView):
    serializer_class = serializers.CommentSerializer

    def post(self, request):
        serializer = serializers.CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            email = User.objects.filter(
                id=Task.objects.filter(
                    id=serializer.data.get('task')
                ).first().user.id
            ).first().email

            send_mail(
                'Subject here',
                f'Your task with id:{serializer.data.get("task")} was commented. Check it please.',
                'daniel.perebinos@mail.ebs-integrator.com',
                [email],
                fail_silently=False,
            )

            return Response({'id': serializer.data.get('id')})

        else:
            return Response({"message": "failed", "details": serializer.errors})


class TaskCommentsView(generics.GenericAPIView):
    serializer_class = serializers.CommentListSerializer

    def get(self, request, pk):
        task = generics.get_object_or_404(Task.objects.filter(pk=pk))
        return Response(serializers.CommentListSerializer(task).data)


class SearchTaskView(generics.ListAPIView):
    serializer_class = serializers.ListTaskSerializer

    def get_queryset(self):
        title = self.request.data.get('title', '')
        return Task.objects.filter(title__contains=title)

    swagger_title = openapi.Parameter('title', openapi.IN_QUERY, description='Searching titles for your input',
                                      type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[swagger_title])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
