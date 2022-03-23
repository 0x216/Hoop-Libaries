import json
import logging
import os
import requests
import time
import random

from celery import Celery
from celery.exceptions import TimeoutError as CeleryTimeoutError

from statsd import StatsClient

from django.conf import settings

from hoop.util.serialization import ModelEncoder

from .exceptions import ServiceError, TimeoutError, NoSuchTaskError

import hoop.hula.conf

TIMEOUT = int(os.environ.get('HULA_TIMEOUT', 5))

queues = {}

logger = logging.getLogger('django')

statsd_client = None
if os.environ.get('STATSD_HOST') and os.environ.get('STATSD_PORT'):
    try:
        statsd_client = StatsClient(os.environ.get('STATSD_HOST'), os.environ.get('STATSD_PORT'))
    except:
        logger.info('ERROR: cannot connect to statsd host')


class Hula(object):
    def __init__(self, server=None, username=None, password=None, timeout=None):
        self.server = server if server else '127.0.0.1'
        self.username = username if username else 'guest'
        self.password = password if password else 'guest'
        self.timeout = timeout or TIMEOUT

        if not server:
            # Standard Docker linking
            if 'HULA_PORT' in os.environ:
                self.server = os.environ['HULA_PORT_5672_TCP_ADDR']

            if os.environ.get('USE_DNS'):
                self.server = 'rabbitmq'

        logger.info(f"Server {self.server}")

        self.queue_id = '{}:{}@{}'.format(self.username, self.password, self.server)

        if self.queue_id not in queues:
            self.queue = Celery(broker='amqp://%s:%s@%s//' % (self.username, self.password, self.server))
            self.queue.config_from_object(hoop.hula.conf)

            queues[self.queue_id] = self.queue
        else:
            self.queue = queues[self.queue_id]

        self.background_calls = {}

    def __getitem__(self, name):
        return self.get(name)

    def statsd_error(self, error_type, service, protocol, task_name):
        if statsd_client:
            statsd_error_event = '{}.{}.{}.{}'.format(error_type, service, protocol, task_name)
            statsd_client.incr(statsd_error_event)

    def make_http_request(self, service, task_name, data):
        protocol = 'http'
        url = 'http://services-%s/%s/' % (service, task_name)

        timer = None

        # timer to send to statsd, strip out periods to prevent subcategories
        task_name_statsd = task_name.replace('.', '_')
        if statsd_client:
            timer = statsd_client.timer('services.{}.{}.{}'.format(service, protocol, task_name_statsd))

        logger.info('[Service Call] %s.%s: Sending HTTP request to %s' % (service, task_name, url))

        start_time = time.time()
        if timer:
            timer.start()

        try:
            response = requests.post(url, data=json.dumps(data, cls=ModelEncoder), timeout=self.timeout)
            if response and response.status_code <= 201:
                response = response.json()
            else:
                self.statsd_error('error', service, protocol, task_name_statsd)
                raise ServiceError(service, task_name, f'Status code: {response.status_code}')

        except requests.exceptions.Timeout as e:
            self.statsd_error('timeout', service, protocol, task_name_statsd)
            logger.warning(e)
            e = TimeoutError(service, task_name)
            raise e
        except requests.exceptions.RequestException as e:
            self.statsd_error('error', service, protocol, task_name_statsd)
            logger.warning(e)
            e = ServiceError(service, task_name)
            raise e

        if isinstance(response, dict) and response.get('status') == 'error':
            self.statsd_error('error', service, protocol, task_name_statsd)
            raise ServiceError(service, task_name, response.get('message'))

        if timer:
            timer.stop()
        logger.info('[Service Call] %s.%s: Succeeded in %.4fs' % (service, task_name, time.time() - start_time))

        return response

    def make_rabbitmq_request(self, service, task, task_name):
        # timer to send to statsd, strip out periods to prevent subcategories
        protocol = 'rabbitmq'
        task_name_statsd = task_name.replace('.', '_')

        timer = None

        if statsd_client:
            timer = statsd_client.timer('services.{}.{}.{}'.format(service, protocol, task_name_statsd))

        start_time = time.time()
        if timer:
            timer.start()
        try:
            response = task.get(timeout=self.timeout)

            if isinstance(response, dict) and response.get('status') == 'error':
                raise ServiceError(service, task_name, response.get('message'))
            else:
                if timer:
                    timer.stop()
                logger.info('[Service Call] %s.%s: Succeeded in %.4fs' % (service, task_name, time.time() - start_time))

                return response

        except CeleryTimeoutError:
            self.statsd_error('timeout', service, protocol, task_name_statsd)
            raise TimeoutError(service, task_name)

        except Exception as e:
            if type(e) is not ServiceError and type(e) is not TimeoutError:
                e = ServiceError(service, task_name)
            self.statsd_error('error', service, protocol, task_name_statsd)

            raise e

    def execute(self, service, method, data={}, version=None, background=False):
        if 'DJANGO_SETTINGS_MODULE' in os.environ and settings.TEST_ENVIRONMENT:
            raise RuntimeError('Test includes Hula call without being mocked')

        # Use new task naming if version given
        if version:
            task_name = '%s.%s' % (version, method)
        else:
            task_name = '%s.tasks.%s' % (service, method)

        # Check if the target service should be
        # communicated with via HTTP yet
        if service in os.environ.get('HTTP_SERVICES', '').split(','):
            http_enabled = True
        else:
            http_enabled = False

        # If it's a background call we should
        # pass it through Rabbit as normal
        if background:
            http_enabled = False

        if http_enabled:
            http_ratio = os.environ.get('HTTP_RATIO', None)
            if http_ratio is None or (http_ratio and random.random() <= float(http_ratio)):
                return self.make_http_request(service, task_name, data)

        logger.info('[Service Call] %s.%s: Using RabbitMQ...' % (service, task_name))

        task = self.queue.send_task(task_name, queue=service, kwargs={'data': data})

        if not background:
            return self.make_rabbitmq_request(service, task, task_name)

        else:
            if isinstance(background, str):
                logger.info(
                    '[Service Call] %s.%s: Background task, storing with key %s' % (service, task_name, background)
                )

                # If background is a string then we store the task so it can be
                # retrieved later using the get() method.
                self.background_calls[background] = {
                    'service': service,
                    'task_name': task_name,
                    'task': task,
                }
            else:
                logger.info('[Service Call] %s.%s: Background task, discarding result' % (service, task_name))

    def get(self, name):
        try:
            task = self.background_calls[name]
        except KeyError:
            raise NoSuchTaskError(name)

        try:
            response = task['task'].get(timeout=self.timeout)
        except CeleryTimeoutError:
            raise TimeoutError(task['service'], task['task_name'])

        if isinstance(response, dict) and response.get('status') == 'error':
            raise Exception('Service Error - %s' % task['task_name'])

        return response
