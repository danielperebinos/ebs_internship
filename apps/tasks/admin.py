from django.contrib import admin
from apps.tasks.models import Task, Comment, TimeLog

# Register your models here.
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(TimeLog)
