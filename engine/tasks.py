import string
import time

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task

@shared_task
def make_cocktail(step,solenoidValve):
    #emulate create cocktail
    time.sleep(30)
    return 'cocktail is complete'