from django.core.management.base import BaseCommand, CommandError
from apps.tasks.models import Task, TimeLog, Status, User
from apps.tasks.elastic import upload_comments_to_elastic, es


class Command(BaseCommand):
    help = 'Will add random 25.000 tasks and 50.000 time logs to your db'

    def add_arguments(self, parser):
        parser.add_argument('--drop', action='store_true',)

    def handle(self, *args, **options):
        if options['drop']:
            es.session.indices.delete(es.text_index)
        upload_comments_to_elastic()
