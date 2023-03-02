from django.contrib import admin

# Register your models here.
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'status_field')
