from django.conf.urls import url

from ..tasks import TaskView

urlpatterns = [url(r'^(?P<task_name>.+)/$', TaskView.as_view())]
