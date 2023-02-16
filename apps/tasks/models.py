from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.core.mail import send_mail


class Task(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()

    class Status(models.TextChoices):
        DONE = 'Done', 'Done'
        IN_PROCESS = 'In Process', 'In Process'
        WAITING = 'Waiting', 'Waiting'

    status_field = models.CharField(max_length=10, choices=Status.choices, default=Status.WAITING)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def send_email(self, body, receivers):
        send_mail('Subject', body, 'daniel.perebinos@mail.ebs-integrator.com', receivers, fail_silently=False)

    def send_email_assign(self):
        self.send_email(f'Task with id:{self.id} was assigned to you. Check it please.', [self.user.email])

    def send_email_to_owner(self):
        self.send_email(f'Your task with id:{self.id} was done. Check it please.', [self.user.email])

    def send_email_to_commenters(self):
        receivers = set([User.objects.filter(id=comment.user.id).first().email
                         for comment in Task.objects.filter(id=self.id).first().comment_set.all()])

        self.send_email(f'Task with id:{self.id} you commented, was done. Check it please.', receivers)


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
