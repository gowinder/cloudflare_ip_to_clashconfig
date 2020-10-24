from django_rq import job
from .models import JobSetting, OpenclashTemplate
from .cloudflare_speed.cf_speed import cf_speed

@job
def tester_task(job_setting_id:int, template_id:int):
    js:JobSetting = JobSetting.objects.get(pk=job_setting_id)
    if js is None:
        return (1, 'job setting not exists')

    setting_dict = js.get_dict()
    if setting_dict is None:
        return (1, 'job setting is not valid')

    tp:OpenclashTemplate = OpenclashTemplate.objects.get(pk=template_id)
    if tp is None:
        return(1, 'Openclash template is not valid')
    
    sp = cf_speed()
    sp.load_config(setting_dict)
    sp.load_ip_list()
    sp.pint()
    sp.speed_test()

