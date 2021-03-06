from django.db.models.fields import reverse_related
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, get_object_or_404

from .models import (
    JobSetting, JobRecord, JobEnv, 
    OpenclashTemplate, SchedulerSetting,
    V2RayConfig)

from django.views.generic import(
    CreateView, DetailView, 
    DeleteView, ListView, UpdateView
    )

import django_rq
from .tasks import run_task
from .scheduler import start_scheduler

def home(request):
    context = {
        'settings': JobSetting.objects.all(),
        'job_records': JobRecord.objects.all(),
        'job_env': JobEnv.objects.first(),
        'title': 'job settings'
    }
    return render(request, 'tester/home.html', context=context)

def duplicate_job_setting(request, pk):
    js = JobSetting.objects.get(pk=pk)
    if js is not None:
        js.pk = None
        js.alias = js.alias + ' copy'
        js.save()
    return home(request)

def activate_job_setting(request, pk):
    js = JobSetting.objects.get(pk=pk)
    if js is not None:
        env = JobEnv.objects.first()
        env.activate_job_setting = pk
        env.save()
    return home(request)

class JobSettingDetailView(DetailView):
    model = JobSetting
    fields = '__all__'
    template_name = 'tester/job_setting_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

from django.forms.models import inlineformset_factory
V2rayFormset = inlineformset_factory(
    JobSetting, V2RayConfig, fields=('alias', 'uuid', 'ws_path', 'host', 'alter_id')
)

class JobSettingCreateView(CreateView):
    model = JobSetting
    fields = '__all__'
    template_name = 'tester/job_setting_form.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data
        # to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["v2rays"] = V2rayFormset(self.request.POST)
        else:
            data["v2rays"] = V2rayFormset()
        return data


    def form_valid(self, form):
        context = form.get_context_data()
        v2rays = context['v2rays']
        self.object = form.save(commit=False)
        if v2rays.is_valid():
            v2rays.instance = self.object
            v2rays.save()
        return super.form_valid(form)
    
    # def get_success_url(self):
    #     return reverse_related('/')


class JobSettingUpdateView(UserPassesTestMixin, UpdateView):
    model = JobSetting
    fields = '__all__'
    template_name = 'tester/job_setting_form.html'
    success_url = '/'
    def form_valid(self, form):
        #form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return True



class JobSettingDeleteView(DeleteView):
    model = JobSetting
    template_name = 'tester/job_setting_delete.html'

    success_url = '/'


def openclash_templates(request):
    context = {
        'templates': OpenclashTemplate.objects.all(),
        'job_env': JobEnv.objects.first(),
        'title': 'OpenClash templates'
    }
    return render(request, 'tester/openclash_templates.html', context=context)


def activate_openclash_template(request, pk):
    tp = OpenclashTemplate.objects.get(pk=pk)
    if tp is not None:
        env = JobEnv.objects.first()
        env.activate_open_clash_template = pk
        env.save()
    return openclash_templates(request)

class OpenclashTemplateDetailView(DetailView):
    model = OpenclashTemplate
    fields = '__all__'
    template_name = 'tester/openclash_template_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class OpenclashTemplateCreateView(CreateView):
    model = OpenclashTemplate
    fields = '__all__'
    template_name = 'tester/openclash_template_form.html'

    def form_valid(self, form):
        #form.instance.author = self.request.user
        return super().form_valid(form)
    
    # def get_success_url(self):
    #     return reverse_related('openclash_templates/')
    success_url = '/openclash_templates/'


class OpenclashTemplateUpdateView(UserPassesTestMixin, UpdateView):
    model = OpenclashTemplate
    fields = '__all__'
    template_name = 'tester/openclash_template_form.html'
    success_url = '/openclash_templates/'
    def form_valid(self, form):
        #form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return True

class OpenclashTemplateDeleteView(DeleteView):
    model = OpenclashTemplate
    template_name = 'tester/openclash_template_delete.html'

    success_url = '/openclash_templates/'

def start_tester_task(request, job_setting_id, template_id):
    django_rq.enqueue(run_task, job_setting_id, template_id)

    return home(request)

class SchedulerSettingUpdateView(UserPassesTestMixin, UpdateView):
    model = SchedulerSetting
    fields = '__all__'
    template_name = 'tester/scheduler_setting_form.html'
    success_url = '/'
    def form_valid(self, form):
        #form.instance.author = self.request.user

        start_scheduler()
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        return True