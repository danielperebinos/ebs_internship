from django.db.models.signals import pre_save, post_init
from django.dispatch import receiver

from apps.tasks.models import Task, Comment


@receiver(pre_save, sender=Task)
def send_email_to_task_owner_trigger(sender, instance, **kwargs):
    if instance.id is not None:
        current = instance
        previous = Task.objects.filter(id=instance.id)
        if previous.count() == 0:
            return
        previous = previous.first()

        if previous.user.id != current.user.id:
            current.send_email_assign()

        if previous.status_field != 'Done' and current.status_field == 'Done':
            current.send_email_to_owner()
            current.send_email_to_commenters()


@receiver(pre_save, sender=Comment)
def send_email_to_task_owner_trigger(sender, instance, **kwargs):
    if instance.id is not None:
        current = instance
        try:
            previous = Comment.objects.get(id=instance.id)
        except Exception:
            current.send_email_to_task_owner()
