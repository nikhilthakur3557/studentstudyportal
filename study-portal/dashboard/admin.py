from django.contrib import admin
from dashboard import models
# Register your models here.

admin.site.register(models.Notes)
admin.site.register(models.HomeWork)
admin.site.register(models.Todo)
