from django.urls import path, include
from . import views
from .views import *


urlpatterns = [
    path('', views.home, name='tester-home'),
    path('job_setting/new/', JobSettingCreateView.as_view(), name='job-setting-create'),
    # path('job_setting/<int:pk>/', JobSettingDetailView.as_view(), name='job-setting-detail'),
    path('job_setting/<int:pk>/update/', JobSettingUpdateView.as_view(), name='job-setting-update'),
    path('job_setting/<int:pk>/delete/', JobSettingDeleteView.as_view(), name='job-setting-delete'),
    path('job_setting/<int:pk>/duplicate/', views.duplicate_job_setting, name='job-setting-duplicate'),
    path('job_setting/<int:pk>/activate/', views.activate_job_setting, name='job-setting-activate'),
    path('openclash_template/new/', OpenclashTemplateCreateView.as_view(), name='openclash-template-create'),
    path('openclash_templates/', views.openclash_templates, name='openclash-template-list'),
    path('openclash_template/<int:pk>/update/', OpenclashTemplateUpdateView.as_view(), name='openclash-template-update'),
    path('openclash_template/<int:pk>/delete/', OpenclashTemplateDeleteView.as_view(), name='openclash-template-delete'),
    path('openclash_template/<int:pk>/activate/', views.activate_openclash_template, name='openclash-template-activate'),
    
    path('django-rq/', include('django_rq.urls')),
    path('start_tester_task/<int:job_setting_id>/<int:template_id>/', views.start_tester_task, name='start-tester-task')
]