from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import response
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.views.generic.base import TemplateView
from .tasks import statUser
from .models import UserTask
from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist

class AdminTaskView(LoginRequiredMixin,UserPassesTestMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'zip_link/task-queue.html'
    title = 'Task queue'

    def test_func(self):
        return self.request.user.is_staff 

class StatisticDataView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'zip_link/stat-doc.html'
    title = 'Statistical data'

    def post(self, *args, **kwargs):
        user_id = self.request.user.id
        try:
            userTask = UserTask.objects.get(user=user_id)
            task = AsyncResult(userTask.task_id)
            #for testing
            #if task.status != 'FAILURE' and userTask.task_end > timezone.now():
                #return response.HttpResponseBadRequest("Function is not available") 
        except ObjectDoesNotExist as Ex:
            userTask = UserTask(user = self.request.user)
        task = statUser.delay(user_id)
        userTask.task_id = task.id
        userTask.task_end = timezone.now() + timedelta(days=1)
        userTask.save()
        return response.HttpResponse("Check status")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        try:
            userTask = UserTask.objects.get(user__id=user_id)
        except ObjectDoesNotExist as Ex:
            return context
        #for testing
        context['restart'] = True
        #context['restart'] = timezone.now() > userTask.task_end
        task = AsyncResult(userTask.task_id)
        context['status'] = task.status
        if task.status == 'SUCCESS':
            context['content'] = task.result
        if task.status == 'FAILURE':
            context['restart'] = True
        return context
