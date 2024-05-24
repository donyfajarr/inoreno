from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.project)
admin.site.register(models.priority)
admin.site.register(models.task)
admin.site.register(models.pic)
admin.site.register(models.feedback)
admin.site.register(models.settings)
admin.site.register(models.status)