from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.tasks import serializers
from rest_framework.response import Response
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
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        email = request.user.email
        serializer = self.get_serializer(instance=instance, data=request.data)


        if serializer.is_valid():
            serializer.save()

            send_mail(
                'Subject here',
                f'Task with id:{serializer.data.get("id")} was assigned to you. Check it please.',
                'daniel.perebinos@mail.ebs-integrator.com',
                [email],
                fail_silently=False,
            )

            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)


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
            emails = set([User.objects.filter(id=comment.user.id).first().email
                      for comment in Task.objects.filter(
                          id=serializer.data.get('id')
                      ).first().comment_set.all()])

            send_mail(
                'Subject here',
                f'Task with id:{serializer.data.get("id")} you commented, was done. Check it please.',
                'daniel.perebinos@mail.ebs-integrator.com',
                emails,
                fail_silently=False,
            )

        return Response(serializer.data)


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
