from django.apps import AppConfig
from .scheduler import start_scheduler
import sys


class TesterConfig(AppConfig):
    name = 'tester'

    def ready(self):
        if 'runserver' in sys.argv:
            start_scheduler()
