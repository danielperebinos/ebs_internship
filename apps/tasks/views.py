from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from apps.tasks.serializers import CreateTaskSerializer, ListTaskSerializer, ViewTaskSerializer
from rest_framework.response import Response
from apps.tasks.models import Task


class CreateTaskView(GenericAPIView):
    serializer_class = CreateTaskSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CreateTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data)


class ListTaskView(ListAPIView):
    serializer_class = ListTaskSerializer
    queryset = Task.objects.all()


class TaskView(RetrieveAPIView):
    serializer_class = ViewTaskSerializer
    queryset = Task.objects.all()
