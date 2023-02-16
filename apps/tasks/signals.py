from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.tasks.models import Task


@receiver(pre_save, sender=Task)
def send_email_to_task_owner_trigger(sender, instance, **kwargs):
    if instance.id is not None:
        current = instance
        print(instance, type(instance))
        previous = Task.objects.get(id=instance.id)
        if previous.user.id != current.user.id:
            current.send_email_assign()

        if previous.status_field != 'Done' and current.status_field == 'Done':
            current.send_email_to_owner()
            current.send_email_to_commenters()
