from django.apps import AppConfig
from .scheduler import start_scheduler

class TesterConfig(AppConfig):
    name = 'tester'

    def ready(self):
        start_scheduler()