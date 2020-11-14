from django_rq import job
from .models import JobSetting, OpenclashTemplate, JobEnv, SchedulerSetting, V2RayConfig
from .cloudflare_speed.cf_speed import cf_speed, util
from django.conf import settings as djangoSettings
from ruamel.yaml import YAML
import yaml
import django_rq

@job
def run_task(job_setting_id:int, template_id:int):
    js:JobSetting = JobSetting.objects.get(pk=job_setting_id)
    if js is None:
        return 1, 'job setting not exists'

    v2ray_list = V2RayConfig.objects.filter(job_setting=js)

    setting_dict = js.get_dict()
    if setting_dict is None:
        return 1, 'job setting is not valid'

    tp:OpenclashTemplate = OpenclashTemplate.objects.get(pk=template_id)
    if tp is None:
        return 1, 'Openclash template is not valid'
    template = yaml.load(tp.template, Loader=yaml.Loader)
    
    sp = cf_speed()
    sp.load_config_from_dict(setting_dict)
    sp.load_ip_list()
    sp.ping()
    sp.speed_test()
    sp.v2ray_list = v2ray_list
    clash = sp.generate_openclash_config(template)
    print('clash=', clash)
    file = djangoSettings.MEDIA_ROOT + 'openclash_generated.yaml'
    util.openclash_to_yaml(clash, file)
    # with open(file, 'w+', encoding='utf-8') as writer:
    #     #yaml.dump(clash, writer, indent=4, mapping=2, sequence=4)
    #     yaml_dump = YAML()
    #     yaml_dump.indent(mapping=2, sequence=4, offset=2)
    #     yaml_dump.compact(seq_seq=True)
    #     yaml_dump.dump(clash, writer)

    return 0, 'success'

