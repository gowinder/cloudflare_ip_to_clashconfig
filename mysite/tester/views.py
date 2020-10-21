from django.db.models.fields import reverse_related
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, get_object_or_404

from .models import JobSetting, JobRecord

from django.views.generic import(
    CreateView, DetailView, DeleteView, ListView, UpdateView
    )


def home(request):
    context = {
        'settings': JobSetting.objects.all(),
        'job_records': JobRecord.objects.all(),
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

class JobSettingDetailView(DetailView):
    model = JobSetting
    fields = '__all__'
    template_name = 'tester/job_setting_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class JobSettingCreateView(CreateView):
    model = JobSetting
    fields = '__all__'
    template_name = 'tester/job_setting_form.html'

    def form_valid(self, form):
        #form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_related('')


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