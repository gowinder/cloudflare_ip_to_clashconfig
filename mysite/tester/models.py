from django.db import models
from django.utils import timezone
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from django.urls import reverse
import uuid

# Create your models here.
class JobSetting(models.Model):
    alias = models.CharField(max_length=50)
    update_time = models.DateTimeField(default=timezone.now)

    cf_ip_list_url = models.CharField(max_length=255)
    cf_ip_list_from_file = models.CharField(max_length=255, blank=True)
    max_ip = models.IntegerField(default=-1)
    ping_thread = models.IntegerField(default=100)
    ping_count = models.IntegerField(default=3)
    speed_test_count = models.IntegerField(default=3)
    speed_host = models.CharField(default='speed.cloudflare.com', max_length=255)
    speed_url = models.CharField(default='/__down?bytes=1000000000', max_length=255)
    download_chunk = models.IntegerField(default=1024)
    download_size = models.IntegerField(default=10485760)
    download_time = models.IntegerField(default=10)

    select_count = models.IntegerField(default=10)

    log_ip_list = models.BooleanField(default=False)
    log_ping = models.BooleanField(default=False)
    log_sorted_ping_list = models.BooleanField(default=False)
    log_speed = models.BooleanField(default=False)
    log_sorted_speed_list = models.BooleanField(default=False)

    oc_dns = models.CharField(default='114.114.114.114', max_length=16)
    oc_use_ip = models.IntegerField(default=3)
    oc_uuid = models.UUIDField(default=uuid.uuid4)
    oc_ws_path = models.CharField(max_length=255)
    oc_host = models.CharField(max_length=16)
    oc_alert_id = models.IntegerField(default=3)

    def __str__(self):
        return self.alias

    def get_absolute_url(self):
        return reverse('job_setting', kwargs={'pk': self.pk})

    def get_yaml(self):
        d = {}
        ip_list = {}
        ip_list['url'] = self.cf_ip_list_url
        ip_list['from_file'] = self.cf_ip_list_from_file
        cloudflare = {}
        cloudflare['ip_list'] = ip_list
        test = {}
        test['max_ip'] = self.max_ip
        test['ping_thread'] = self.ping_thread
        test['ping_count'] = self.ping_count
        test['speed_test_count'] = self.speed_test_count
        test['host'] = self.speed_host
        test['url'] = self.speed_url
        test['download_chunk'] = self.download_chunk
        test['download_size'] = self.download_size
        test['download_time'] = self.download_time
        cloudflare['test'] = test

        result = {}
        result['select_count'] = self.select_count
        cloudflare['result'] = result

        l = {}
        l['ip_list'] = self.log_ip_list
        l['ping'] = self.log_ping
        l['sorted_ping_list'] = self.log_sorted_ping_list
        l['speed'] = self.log_speed
        l['sorted_speed_list'] = self.log_sorted_speed_list
        cloudflare['log'] = l

        d['cloudflare'] = cloudflare

        oc = {}
        oc['dns'] = self.oc_dns
        oc['use_ip'] = self.oc_use_ip
        oc['uuid'] = self.oc_uuid
        oc['ws-path'] = self.oc_ws_path
        oc['host'] = self.oc_host
        oc['alterId'] = self.oc_alert_id 
        d['openclash'] = oc
        
        yaml_dump = YAML()
        yaml_dump.indent(mapping=2, sequence=4, offset=2)
        stream = StringIO()
        yaml_dump.dump(d, stream)
        return stream.getValue()

class JobEnv(models.Model):
    number = models.IntegerField(default=0)
    curent_job = models.IntegerField(default=-1)
    activate_job_setting = models.IntegerField(default=-1)

class JobRecord(models.Model):
    number = models.IntegerField()
    time = models.DateTimeField()
    status = models.IntegerField()
    log = models.TextField()
