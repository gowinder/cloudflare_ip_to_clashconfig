import sys
#sys.path.append('..')
import os
import pathlib
from django_rq import jobs
import pytest
from django.utils import timezone
from .models import JobSetting, V2RayConfig, OpenclashTemplate
from .tasks import run_task
from django.conf import settings
from mysite.settings import BASE_DIR
from django.core.management import call_command
from django.conf import settings as djangoSettings
from .cloudflare_speed.util import util


USE_IP = 3
USE_V2RAY = 3

LOG_SORTED_PING_LIST = True
LOG_SPEED = True
LOG_SORTED_SPEED_LIST = True
CF_IP_URL = 'https://www.cloudflare.com/ips-v4'
IP_LIST_FILE = os.path.join(pathlib.Path(__file__).parent.absolute(), 'cloudflare_speed/ip_list.txt')

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
       job_setting_alias = 'default_test'
       with django_db_blocker.unblock():
            call_command('migrate')
            JobSetting.objects.all().delete()
            JobSetting.objects.create(
               alias=job_setting_alias,
               cf_ip_list_url=CF_IP_URL,
               cf_ip_list_from_file=IP_LIST_FILE,
               oc_use_ip=USE_IP,
               log_sorted_ping_list=LOG_SORTED_PING_LIST,
               log_speed=LOG_SPEED,
               log_sorted_speed_list=LOG_SORTED_SPEED_LIST)

            assert JobSetting.objects.count() == 1
            assert JobSetting.objects.first().alias == job_setting_alias

            V2RayConfig.objects.all().delete()
            V2RayConfig.objects.create(
                alias='v1',
                uuid='v1-uuid',
                ws_path='v1-ws_path',
                host='v1-host',
                alter_id=1,
                job_setting=JobSetting.objects.first()
            )
            V2RayConfig.objects.create(
                alias='v2',
                uuid='v2-uuid',
                ws_path='v2-ws_path',
                host='v2-host',
                alter_id=2,
                job_setting=JobSetting.objects.first()
            )
            V2RayConfig.objects.create(
                alias='v3',
                uuid='v3-uuid',
                ws_path='v3-ws_path',
                host='v3-host',
                alter_id=3,
                job_setting=JobSetting.objects.first()
            )

            assert V2RayConfig.objects.count() == 3
            for v2ray in V2RayConfig.objects.all():
                if v2ray.alias == 'v1':
                    assert v2ray.uuid == 'v1-uuid'
                elif v2ray.alias == 'v2':
                    assert v2ray.uuid == 'v2-uuid'
                if v2ray.alias == 'v3':
                    assert v2ray.uuid == 'v3-uuid'
            
            template_text = ''
            template_file = \
                os.path.join(pathlib.Path(__file__).parent.absolute(), \
                     '../../openclash.template.yaml')
            with open(template_file, 'r', encoding='utf-8') as f:
                template_text = f.read()
            assert template_text != ''
            OpenclashTemplate.objects.all().delete()
            OpenclashTemplate.objects.create(
                alias='default',
                template=template_text
            )
            assert OpenclashTemplate.objects.first().alias == 'default'

@pytest.mark.django_db
def test_tasks():
    job_setting_id = JobSetting.objects.first().pk
    template_id = OpenclashTemplate.objects.first().pk
    print('job_setting_id=', job_setting_id, 'template_id=', template_id)
    code, msg = run_task(job_setting_id, template_id)
    assert code == 0
    assert msg == 'success'
    file = djangoSettings.MEDIA_ROOT + 'openclash_generated.yaml'
    data = util.load_yaml_file(file)
    assert data != None
    proxy_group = data['Proxy Group']
    assert proxy_group != None
    assert len(proxy_group) > 0
    auto = proxy_group[0]
    assert auto['proxies'] != None
    assert len(auto['proxies']) == USE_IP * USE_V2RAY