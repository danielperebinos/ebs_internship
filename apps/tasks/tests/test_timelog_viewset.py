from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from apps.tasks import serializers
from apps.tasks.models import TimeLog


class CommentViewTest(APITestCase):
    fixtures = ['user.json', 'task.json', 'comment.json', 'timelog.json']

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.get(username="users")
        self.client.force_authenticate(user=self.user)

    def test_start_timer(self):
        task_id = 1
        url = reverse('timelog-start')
        data = {'task': task_id}
        query_params = ''.join([f'{key}={value}&' for key, value in data.items()])
        response = self.client.put(url, QUERY_STRING=query_params)
        self.assertEqual(response.status_code, 200)

    def test_stop_time(self):
        task_id = 2
        url = reverse('timelog-stop')
        data = {'task': task_id}
        query_params = ''.join([f'{key}={value}&' for key, value in data.items()])
        response = self.client.put(url, QUERY_STRING=query_params)
        self.assertEqual(response.status_code, 200)

        serializer = serializers.TimeLogSerializer(TimeLog.objects.filter(task_id=task_id).order_by('-start').first())
        self.assertEqual(response.data, serializer.data)

    def test_get_logs_of_task(self):
        task_id = 1
        url = reverse('timelog-list')
        data = {'task': task_id}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)

        serializer = serializers.TimeLogSerializer(TimeLog.objects.filter(task_id=task_id), many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_log(self):
        url = reverse('timelog-list')
        data = {'start': '2023-02-22T09:37:25Z',
                'duration': 60,
                'task': 1}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(dict(response.data), data)

    def test_get_my_logged_time(self):
        url = reverse('timelog-my-logged-time')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        month, year = TimeLog.prev_ym()
        logs = TimeLog.objects.filter(user=self.user, start__year=year, start__month=month)
        durations = logs.values_list('duration', flat=True)
        time = sum(durations)

        self.assertEqual(response.json().get('duration'), time)