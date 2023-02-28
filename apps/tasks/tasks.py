from rest_framework import generics
from huey.contrib.djhuey import task

from apps.tasks.models import Status


@task(name='assign_task', priority=4)
def assign_task(pk, user, serializer, queryset):
    instance = generics.get_object_or_404(queryset, id=pk)
    serializer = serializer(instance=instance, data={'user': user}, partial=True)

    if serializer.is_valid():
        serializer.save()


@task(name='update_task_status', priority=3)
def update_task_status(pk, data, serializer, queryset):
    instance = generics.get_object_or_404(queryset, id=pk)
    serializer = serializer(instance, data=data)

    if serializer.is_valid():
        serializer.save()


@task(name='complete_task', priority=3)
def complete_task(pk, serializer, queryset):
    instance = generics.get_object_or_404(queryset, id=pk)
    serializer = serializer(instance, data={'status_field': Status.DONE}, partial=True)

    if serializer.is_valid():
        serializer.save()
