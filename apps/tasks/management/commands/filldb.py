from django.core.management.base import BaseCommand, CommandError
from apps.tasks.models import Task, TimeLog, Status, User
import datetime
import random
import string


class Command(BaseCommand):
    help = 'Will add random 25.000 tasks and 50.000 time logs to your db'

    def add_arguments(self, parser):
        parser.add_argument('user', type=int)

    def handle(self, *args, **options):
        if not options.get('user'):
            raise Exception('Not user added')

        for task_index in range(25000):

            temp = Task.objects.create(
                title=self.random_text(15),
                description=self.random_text(30),
                status_field=self.random_status(),
                user=User.objects.get(id=options['user']),
            )

            for timelog_index in range(2):
                TimeLog.objects.create(
                    start=self.random_date(datetime.datetime(day=1, month=1, year=2019), datetime.datetime.now()),
                    duration=random.randrange(0, 500),
                    user=User.objects.get(id=options['user']),
                    task=temp
                )

    def random_text(self, length):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def random_date(self, start, end):
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        return (start + datetime.timedelta(seconds=random_second)).isoformat()

    def random_status(self):
        return random.choice(Status.choices)[0]