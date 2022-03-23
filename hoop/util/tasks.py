import json
import importlib
import celery
import inspect

from celery.app.task import TaskType
from celery.local import Proxy

from django.apps import apps
from django.http import Http404, JsonResponse
from django.views.generic import View

from sentry_sdk import capture_exception, configure_scope

from hoop.util.serialization import ModelEncoder

TASK_MAP = {}


def __find_modules(sub_package_name):
    mods = []
    for app in apps.get_app_configs():
        # check if we can import the module
        package = app.name
        try:
            importlib.import_module(app.name)
        except ImportError:
            # try the one above
            package, _, _ = package.rpartition(".")
            if not package:
                raise
        try:
            mod = importlib.import_module('{}.{}'.format(package, sub_package_name))
            mods.append(mod.__name__)
        except ImportError:
            continue
    return mods


def __discover_tasks():
    task_mappings = {}
    task_modules = __find_modules("tasks")

    for mod in task_modules:
        imported_mod = importlib.import_module(mod)
        for name, data in inspect.getmembers(imported_mod):
            if name != '__builtins__':
                if type(data) is Proxy or type(data) is TaskType:
                    task_mappings[data.name] = getattr(imported_mod, name)

    return task_mappings


def run_task(task_name, data):
    # We need to lazy load the tasks once
    # as it's a pretty slow operation
    if not TASK_MAP:
        TASK_MAP.update(__discover_tasks())

    # Now we can fetch the task, but it may
    # be class based or a legacy function task
    task = TASK_MAP.get(task_name)

    # Check if we have a function based task
    if isinstance(task, Proxy):
        return task(data=data)

    # Or a class based one
    elif isinstance(task, TaskType):
        return task().run(data=data)

    # Couldn't find anything to run!
    else:
        raise Http404


class TaskView(View):
    def dispatch(self, request, task_name):
        data = {}

        if request.method == 'GET':
            data = request.GET.dict()
        elif request.body:
            data = json.loads(request.body.decode('utf-8'))

        with configure_scope() as scope:
            scope.transaction = task_name

        return JsonResponse(run_task(task_name, data=data), safe=False, encoder=ModelEncoder)
