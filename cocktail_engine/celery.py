import os
from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktail_engine.settings')

app = Celery('cocktail_engine', backend='amqp', broker='amqp://guest@localhost//')
app.config_from_object('django.conf:settings', )
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
