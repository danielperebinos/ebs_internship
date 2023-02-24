from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from apps.tasks import serializers
from apps.tasks.models import Comment


class CommentViewTest(APITestCase):
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
