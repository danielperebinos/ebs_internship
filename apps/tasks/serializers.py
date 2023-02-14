from rest_framework import serializers
from apps.tasks.models import Task
from apps.users.serializers import UserReadSerializer


class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('title', 'description', 'status_field')


class ViewTaskSerializer(serializers.ModelSerializer):
    user = UserReadSerializer()

    class Meta:
        model = Task
        fields = ('__all__')


class ListTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title')
