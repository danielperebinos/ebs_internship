from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from apps.tasks import serializers
from rest_framework.response import Response
from apps.tasks.models import Task
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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
        serializer = self.get_serializer(instance=instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
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

        return Response(serializer.data)


class DeleteTaskView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = serializers.UpdateStatusTaskSerializer
    lookup_field = 'pk'


