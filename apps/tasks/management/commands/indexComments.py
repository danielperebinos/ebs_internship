from django.core.management.base import BaseCommand, CommandError
from apps.tasks.models import Task, TimeLog, Status, User
from apps.tasks.elastic import upload_comments_to_elastic


class Command(BaseCommand):
    help = 'Will add random 25.000 tasks and 50.000 time logs to your db'

    def handle(self, *args, **options):
        upload_comments_to_elastic()
