from django.contrib import admin
from .models import Authors, News

# Register your models here.

admin.site.register(Authors)
admin.site.register(News)