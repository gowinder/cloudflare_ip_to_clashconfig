from django.contrib import admin
from .models import (JobSetting, JobEnv, JobRecord)
# Register your models here.

admin.site.register(JobSetting)
admin.site.register(JobEnv)
admin.site.register(JobRecord)