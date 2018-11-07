import string
import time

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from celery import shared_task, current_task


@shared_task()
def make_cocktail(dict):
    # emulate create cocktail
    # send dose
    time.sleep(5)
    current_task.update_state(
        state='PROGRESS_STATE',
        meta={
            'total': 20,
        })
    # move tray
    time.sleep(30)
    current_task.update_state(
        state='PROGRESS_STATE',
        meta={
            'total': 60,
        })
    # send dose
    time.sleep(10)
    current_task.update_state(
        state='PROGRESS_STATE',
        meta={
            'total': 80,
        })
    time.sleep(10)
    return {'total': 100}
