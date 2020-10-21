from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('', views.home, name='tester-home'),
    path('job_setting/new/', JobSettingCreateView.as_view(), name='job-setting-create'),
    path('job_setting/<int:pk>/', JobSettingDetailView.as_view(), name='job-setting-detail'),
    path('job_setting/<int:pk>/update/', JobSettingUpdateView.as_view(), name='job-setting-update'),
    path('job_setting/<int:pk>/delete/', JobSettingDeleteView.as_view(), name='job-setting-delete'),
    path('job_setting/<int:pk>/duplicate/', views.duplicate_job_setting, name='job-setting-duplicate'),

]