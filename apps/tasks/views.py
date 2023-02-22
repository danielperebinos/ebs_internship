from django.db import models
from rest_framework import generics, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from apps.tasks import serializers
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema, no_body
from apps.tasks.models import Task, TimeLog, Status, Comment

import datetime


class TaskViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Task.objects.all()

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'id': serializer.data.get('id')}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], description='Get my tasks')
    def my(self, request, **kwargs):
        my_tasks = Task.objects.filter(user=request.user)
        serializer = self.get_serializer(my_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], description='Get completed tasks', url_name='completed_tasks')
    def completed(self, request, **kwargs):
        my_tasks = Task.objects.filter(status_field=Status.DONE)
        serializer = self.get_serializer(my_tasks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], description='Assign a task to a user')
    def assign(self, request, **kwargs):
        instance = generics.get_object_or_404(self.get_queryset(), id=kwargs.get('pk'))
        serializer = self.get_serializer(instance=instance, data={'user': request.data.get('user')}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            Response(serializer.errors)

    @action(detail=True, methods=['put'])
    def update_status(self, request, **kwargs):
        instance = generics.get_object_or_404(self.get_queryset(), id=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            Response(serializer.errors)

    @swagger_auto_schema(request_body=no_body)
    @action(detail=True, methods=['put'])
    def complete(self, request, **kwargs):
        instance = generics.get_object_or_404(self.get_queryset(), id=kwargs.get('pk'))
        serializer = self.get_serializer(instance, data={'status_field': Status.DONE}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            Response(serializer.errors)

    @swagger_auto_schema(query_serializer=serializers.ListTaskSerializer())
    @action(detail=False, methods=['get'])
    def search_by_title(self, request, **kwargs):
        title = request.query_params.get('title', '')
        searched_tasks = Task.objects.filter(title__contains=title)
        serializer = self.get_serializer(searched_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_20(self, request, *args, **kwargs):
        tasks = self.get_queryset().values('id', 'title').annotate(duration=models.Sum('timelog__duration')).order_by('-duration')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateTaskSerializer
        if self.action == 'retrieve':
            return serializers.ViewTaskSerializer
        if self.action == 'list':
            return serializers.TaskDurationSerializer
        if self.action in ['my', 'completed', 'search_by_title']:
            return serializers.ListTaskSerializer
        if self.action == 'assign':
            return serializers.UpdateUserTaskSerializer
        if self.action in ['update_status', 'complete']:
            return serializers.UpdateStatusTaskSerializer
        if self.action == 'top_20':
            return serializers.TaskDurationSerializer
        return serializers.ViewTaskSerializer


class CommentViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response({"message": "failed", "details": serializer.errors})

    @swagger_auto_schema(query_serializer=serializers.TaskCommentSerializer())
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        task_id = self.request.query_params.get('task_id')
        return queryset.filter(task__id=task_id)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CommentSerializer
        if self.action == 'list':
            return serializers.ReadCommentSerializer
        return serializers.CommentSerializer


class TimerLogViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = TimeLog.objects.all()

    @swagger_auto_schema(request_body=no_body, query_serializer=serializers.GetTaskTimeLogSerializer())
    @action(detail=False, methods=['put'])
    def start(self, request, *args, **kwargs):
        pk = request.query_params.get('task_id')
        if self.get_queryset().filter(task=pk, user=request.user.id, duration=0).count() > 0:
            return Response({"message": "Already exists an other timer, you should close."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data={'user': request.user.id, 'task': pk}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Timer start successfully"})

        else:
            return Response({"message": "failed", "details": serializer.errors})

    @swagger_auto_schema(query_serializer=serializers.GetTaskTimeLogSerializer(), request_body=no_body)
    @action(detail=False, methods=['put'])
    def stop(self, request, *args, **kwargs):
        instance = generics.get_object_or_404(self.get_queryset(), task=request.query_params.get('task_id'),
                                              user=request.user.id, duration=0)

        duration = (datetime.datetime.now() - instance.start.replace(tzinfo=None)).seconds // 60

        serializer = self.get_serializer(instance=instance,
                                         data={'duration': duration if duration else 1},
                                         partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)

    @swagger_auto_schema(query_serializer=serializers.GetTaskTimeLogSerializer(), request_body=no_body)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response({"message": "failed", "details": serializer.errors})

    @action(detail=False, methods=['get'])
    def my_logged_time(self, request, *args, **kwargs):
        month, year = TimeLog.prev_ym()

        logs = TimeLog.objects.filter(user=request.user, start__year=year, start__month=month)
        durations = logs.values_list('duration', flat=True)
        time = sum(durations)

        return Response({'duration': time})

    @action(detail=False, methods=['get'])
    def top_20(self, request, *args, **kwargs):
        logs = TimeLog.objects.all().order_by('-duration')[:20]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        return queryset.filter(task=self.request.query_params.get('task_id'))

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateTimeLogSerializer
        return serializers.TimeLogSerializer
