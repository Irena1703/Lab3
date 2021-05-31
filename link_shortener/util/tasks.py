from celery import shared_task, Task
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone, dateformat
from django.core.mail import send_mass_mail
from zip_link.models import Link
import time
from django.db.models import Avg, Max, Min, Sum

class BaseTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        "tasks", {
            'type' : "task",
             "name" : self.name.split(".")[-1] + "[%s]" % task_id[:8],
             "args" : str(args),
             "result" : "Success",
             "time" : "%s" % (dateformat.format(timezone.localtime(timezone.now()), "Y-m-d H:i:s")), 
        })
        return super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        "tasks", {
            'type' : "task",
             "name" : self.name.split(".")[-1] + "[%s]" % task_id[:8],
             "args" : str(args),
             "result" : "Failure:[%s]" % str(einfo),
             "time" : "%s" % (dateformat.format(timezone.localtime(timezone.now()), "Y-m-d H:i:s")),
        })
        return super().on_failure(exc, task_id, args, kwargs, einfo)

@shared_task(bind=True,default_retry_delay=300, max_retries=5, base=BaseTask, ignore_result=True)
def mailGroup(self, group_id, subject, text):
    group = User.objects.filter(groups__id=group_id)
    emails = list()
    for user in group:
        emails.append((subject, text, None, [user.email]))
    try:
        #need smtp server
        #send_mass_mail(emails, fail_silently=False)
        time.sleep(3)
        return
    except Exception as e:#If network error
        self.retry(e)

header = """
<div class="card">
        <div class="card-body">
            <h4 class="card-title">Profile statistics</h4>
            <table class="table">
        """
end =   """ 
            </table>
        </div>
    </div>
        """

def html_stat(avg, max, min, sum, count):
    return header + f"""
     <tr>
            <td>Number of links</td>
            <td>{count}</td>
     </tr>
     <tr>
            <td>Average counter</td>
            <td>{avg}</td>
     </tr>
      <tr>
            <td>Max counter</td>
            <td>{max}</td>
     </tr>
      <tr>
            <td>Min counter</td>
            <td>{min}</td>
     </tr>
      <tr>
            <td>Sum</td>
            <td>{sum}</td>
     </tr>
    """ + end



@shared_task(base=BaseTask)
def statUser(user_id):
    links = Link.objects.filter(user__id = user_id).order_by('-counter')
    count = links.count()
    data = links.aggregate(Avg('counter'),Max('counter'), Min('counter'), Sum('counter') )
    result = html_stat(data["counter__avg"], data["counter__max"], data["counter__min"], \
        data["counter__sum"], count)
    time.sleep(1)
    return result