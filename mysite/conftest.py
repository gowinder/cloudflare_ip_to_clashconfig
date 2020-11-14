from mysite.settings import BASE_DIR
import pytest
from django.conf import settings
import os
from django.core.management import call_command

# @pytest.fixture(scope='session')
# def django_db_setup():
#     settings.DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
#     }


@pytest.fixture(scope='session')
def django_db_setup():
    from django.conf import settings

    settings.DATABASES['default']['NAME'] = os.path.join(BASE_DIR, 'test_db.sqlite3')
    
        

