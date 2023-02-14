from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()

    class Status(models.TextChoices):
        DONE = 'Done', 'Done'
        IN_PROCESS = 'In Process', 'In Process'
        WAITING = 'Waiting', 'Waiting'

    status_field = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
