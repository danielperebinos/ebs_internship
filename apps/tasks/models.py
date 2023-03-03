from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.mail import send_mail
from django.utils import timezone
from mongoengine import Document, fields


def custom_send_email(body, receivers):
    send_mail('Subject', body, 'daniel.perebinos@mail.ebs-integrator.com', receivers, fail_silently=False)


class Status(models.TextChoices):
    DONE = 'Done', 'Done'
    IN_PROCESS = 'In Process', 'In Process'
    WAITING = 'Waiting', 'Waiting'


class Task(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()

    status_field = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def send_email_assign(self):
        custom_send_email(f'Task with id:{self.id} was assigned to you. Check it please.', [self.user.email])

    def send_email_to_owner(self):
        custom_send_email(f'Your task with id:{self.id} was done. Check it please.', [self.user.email])

    def send_email_to_commenters(self):
        receivers = set(Task.objects.get(id=self.id).comment_set.all().values_list('user__email', flat=True))
        custom_send_email(f'Task with id:{self.id} you commented, was done. Check it please.', receivers)

    def duration(self):
        return sum(self.timelog_set.all().values_list('duration', flat=True))


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def send_email_to_task_owner(self):
        receiver = self.task.user.email
        custom_send_email(f'Task with id:{self.task} was commented by user with id:{self.user.id}. Check it please.',
                          receiver)


class TimeLog(models.Model):
    start = models.DateTimeField(default=timezone.now())
    duration = models.IntegerField(default=0)

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    @classmethod
    def prev_ym(cls):
        today = datetime.datetime.today()
        if today.month - 1 > 0:
            prev_month = today.month - 1
            year = today.year
        else:
            prev_month = 12
            year = today.year - 1

        return prev_month, year


class Goal(Document):
    text = fields.StringField()
    relevancy = fields.IntField()
