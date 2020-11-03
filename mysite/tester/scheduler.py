


def start_scheduler():
    # import here not at the top of the file
    from .models import JobEnv, SchedulerSetting
    from .tasks import tester_task
    import django_rq
    from datetime import datetime
    job_env = JobEnv.objects.first()
    scheduler_setting = SchedulerSetting.objects.first()
    if scheduler_setting is not None \
    and job_env.activate_job_setting != -1 \
    and job_env.activate_open_clash_template != -1:
        
        sch = django_rq.get_scheduler('default')
        jobs = sch.get_jobs()
        for job in jobs:
            sch.cancel(job)
            
        sch.schedule(
            scheduled_time=datetime.utcnow(), # Time for first execution, in UTC timezone
            func=tester_task,                     # Function to be queued
            args=[job_env.activate_job_setting, job_env.activate_open_clash_template],             # Arguments passed into function when executed
            kwargs={},         # Keyword arguments passed into function when executed
            interval=scheduler_setting.interval,                   # Time before the function is called again, in seconds
            repeat=None,                     # Repeat this number of times (None means repeat forever)
            meta={}            # Arbitrary pickleable data on the job itself
        )
