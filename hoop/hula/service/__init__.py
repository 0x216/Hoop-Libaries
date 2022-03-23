import os

from celery import Celery
from celery.signals import celeryd_init

from django.conf import settings

from hoop.hula import conf, sentry
from hoop.util import env, serialization

# Make sure our Django config can be found
os.environ['DJANGO_SETTINGS_MODULE'] = 'hoop.hula.service.settings'

# Check if Docker is passing a RabbitMQ host
if 'HULA_PORT' in os.environ:
    broker = os.environ['HULA_PORT_5672_TCP_ADDR']
elif os.environ.get('USE_DNS'):
    broker = 'rabbitmq'
else:
    broker = '127.0.0.1'

# Now connect & setup the Celery app
app = Celery('service', broker=broker)

# Update Celery config
app.config_from_object(conf)
app.conf.update(CELERY_RESULT_SERIALIZER='hoop-json')

# Autodiscover the tasks using our Django config
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configuration when worker starts up
celeryd_init.connect(sentry.init)
