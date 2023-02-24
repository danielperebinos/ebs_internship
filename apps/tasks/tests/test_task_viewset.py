from django.db import models
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from apps.tasks import serializers
from apps.tasks.models import Task, Status


class TaskViewTest(APITestCase):
    fixtures = ['timelog.json', 'user.json', 'task.json']

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.get(username="users")
        self.client.force_authenticate(user=self.user)

    def test_get_task_list(self):
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        serializer = serializers.TaskDurationSerializer(Task.objects.all(), many=True)
        self.assertListEqual(response.data, serializer.data)

    def test_create_task(self):
        url = reverse('task-list')
        data = {
            'title': 'test1',
            'description': 'test description',
            'status_field': 'Done',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)

        data['id'] = response.json().get('id')
        serializer = serializers.CreateTaskSerializer(Task.objects.get(id=data['id']))
        self.assertDictEqual(dict(serializer.data), data)

    def test_get_my_tasks(self):
        url = reverse('task-my')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        tasks = Task.objects.filter(user=self.user)
        serializer = serializers.ListTaskSerializer(tasks, many=True)
        self.assertListEqual(response.data, serializer.data)

    def test_get_completed_tasks(self):
        url = reverse('task-completed_tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        tasks = Task.objects.filter(status_field=Status.DONE)
        serializer = serializers.ListTaskSerializer(tasks, many=True)
        self.assertListEqual(response.data, serializer.data)

    def test_assign_task_to_user(self):
        id = 1
        url = reverse('task-assign', kwargs={'pk': id})
        data = {
            'user': 2,
            'id': id
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)

        serializer = serializers.UpdateUserTaskSerializer(Task.objects.get(id=id))
        self.assertDictEqual(dict(serializer.data), data)

    def test_update_task_status(self):
        id = 1
        url = reverse('task-update-status', kwargs={'pk': id})
        data = {
            'status_field': str(Status.WAITING),
            'id': id
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)

        serializer = serializers.UpdateStatusTaskSerializer(Task.objects.get(id=id))
        self.assertDictEqual(dict(serializer.data), data)

    def test_complete_task(self):
        id = 1
        url = reverse('task-complete', kwargs={'pk': id})
        data = {
            'status_field': str(Status.DONE),
            'id': id
        }
        response = self.client.put(url)
        self.assertEqual(response.status_code, 200)

        serializer = serializers.UpdateStatusTaskSerializer(Task.objects.get(id=id))
        self.assertDictEqual(serializer.data, data)

    def test_search_task_by_title(self):
        url = reverse('task-search-by-title')
        data = {'title': 'task'}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)

        tasks = Task.objects.filter(title__contains=data['title'])
        serializer = serializers.ListTaskSerializer(tasks, many=True)
        self.assertListEqual(response.data, serializer.data)

    def test_get_top_20_tasks(self):
        url = reverse('task-top-20')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        tasks = Task.objects.all().values('id', 'title').annotate(duration=models.Sum('timelog__duration')).order_by(
            '-duration')[:20]
        serializer = serializers.TaskDurationSerializer(tasks, many=True)
        self.assertListEqual(response.data, serializer.data)



