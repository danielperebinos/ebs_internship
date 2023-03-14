import datetime

from rest_framework import serializers
from rest_framework_mongoengine import serializers as mongo_serializers
from apps.tasks.models import Task, Comment, TimeLog, Goal
from apps.users.serializers import UserReadSerializer


######################
# Tasks
class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status_field')
        read_only = ('id',)


class ViewTaskSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()

    class Meta:
        model = Task
        fields = ('__all__')


class ListTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title')
        read_only = ('id',)


class UpdateUserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'user',)


class UpdateStatusTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'status_field',)


######################
# Comments
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'task', 'text')


class ReadCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'task', 'text')
        read_only = ('id', 'text',)


class TaskCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'task')
        read_only = ('id',)


class SimpleCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text')
        read_only = ('id',)


######################
# Time Logs
class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('start', 'duration', 'task', 'user')


class CreateTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('start', 'duration', 'task')


class TaskDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'duration')


class GetTaskTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('id', 'task')
        read_only = ('id',)


class ScheduleTimeLogSerializer(serializers.ModelSerializer):
    stop = serializers.DateTimeField()

    class Meta:
        model = TimeLog
        fields = ('id', 'task', 'stop')
        read_only = ('id',)


######################
# Goals
class GoalSerializer(mongo_serializers.DocumentSerializer):
    class Meta:
        model = Goal
        fields = '__all__'


######################
# Countries
class CountrySerializer(serializers.Serializer):
    alpha_2 = serializers.CharField(min_length=2, max_length=3)
    phone_code = serializers.CharField(min_length=2, max_length=10)
    name_language = serializers.DictField(child=serializers.CharField())
