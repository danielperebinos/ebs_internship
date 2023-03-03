from time import sleep

from django.conf import settings
from django.urls import reverse
from django.test import TestCase
from django.db import models
from fixtures_mongoengine import FixturesMixin
from rest_framework.test import APIClient

from django.contrib.auth.models import User
from django.core.management import call_command

from apps.tasks import serializers
from apps.tasks.models import Comment, Task, TimeLog, Status, Goal
from apps.tasks.fixtures.goal import FixtureGoal
from config.elastic import es


class CommentViewTest(TestCase):
    fixtures = ['user.json', 'task.json', 'comment.json']

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.get(username="users")
        self.client.force_authenticate(user=self.user)

    def test_get_comments_list(self):
        task_id = 1
        url = reverse('comment-list')
        data = {'task': task_id}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)

        serializer = serializers.ReadCommentSerializer(Comment.objects.filter(task=task_id), many=True)
        self.assertListEqual(response.data, serializer.data)

    def test_create_comment(self):
        task_id = 1
        url = reverse('comment-list')
        data = {
            'task': task_id,
            'text': 'test text',
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

        data['id'] = response.json().get('id')
        serializer = serializers.CommentSerializer(Comment.objects.get(id=data['id']))
        self.assertDictEqual(dict(serializer.data), data)


class TaskViewTest(TestCase):
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


class TimeLogViewTest(TestCase):
    fixtures = ['user.json', 'task.json', 'timelog.json']

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


class GoalViewTest(TestCase, FixturesMixin):
    fixtures = ['user.json']
    fixtures_conf = {
        'goals': FixtureGoal
    }

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.get(username="users")
        self.client.force_authenticate(user=self.user)

    def test_list_goals(self):
        url = reverse('goal-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        serializer = serializers.GoalSerializer(Goal.objects(), many=True)
        self.assertEqual(response.data, serializer.data)

    def test_create_goal(self):
        url = reverse('goal-list')
        goal = {
            'text': 'string string string',
            'relevancy': 2
        }
        response = self.client.post(url, data=goal)
        self.assertEqual(response.status_code, 201)

        id = response.json().get('id')
        serializer = serializers.GoalSerializer(Goal.objects.get(id=id))

        self.assertEqual(response.data, serializer.data)

    def test_retrieve_goal(self):
        goal_id = Goal.objects.first().id
        url = reverse('goal-detail', kwargs={'id': goal_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_update_goal_put(self):
        goal = Goal.objects.first()
        url = reverse('goal-detail', kwargs={'id': goal.id})
        data = {
            'relevancy': 10
        }

        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)
        serializer = serializers.GoalSerializer(Goal.objects.first())
        self.assertEqual(response.data, serializer.data)

    def test_update_goal_patch(self):
        goal = Goal.objects.first()
        url = reverse('goal-detail', kwargs={'id': goal.id})
        data = {
            'relevancy': 10
        }

        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)
        serializer = serializers.GoalSerializer(Goal.objects.first())
        self.assertEqual(response.data, serializer.data)

    def test_delete_goal(self):
        goal = Goal.objects.first()
        url = reverse('goal-detail', kwargs={'id': goal.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ElasticSearchTest(TestCase):
    fixtures = ['user.json', 'task.json', 'comment.json']

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.get(username="users")
        self.client.force_authenticate(user=self.user)

        self.es = es
        self.es.index_prefix = settings.ELASTIC_TEST_INDEX_PREFIX
        self.es.build_index_names()
        self.es.init_indexes()
        call_command('indexComments', '--drop')
        sleep(1)

    def tearDown(self) -> None:
        es.session.indices.delete(es.text_index)
        self.es.index_prefix = settings.ELASTIC_INDEX_PREFIX
        self.es.build_index_names()

    def test_indexes(self):
        self.assertIn(self.es.text_index, self.es.session.indices.get('*').keys())

    def test_search_by_text(self):
        url = reverse('comment-search-by-text')
        data = {'text': 'finibus'}

        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)

        comments = Comment.objects.filter(text__contains=data['text'])
        serializer = serializers.CommentSerializer(comments, many=True)
        self.assertEqual([dict(element) for element in serializer.data], response.data.get('comments'))
