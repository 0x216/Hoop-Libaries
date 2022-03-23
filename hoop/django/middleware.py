import os
import logging
from statsd import StatsClient

from django.conf import settings

logger = logging.getLogger('django')


class StatsdMiddleware:
    def __init__(self, get_response):
        self.statsd_client = None

        if os.environ.get('STATSD_HOST') and os.environ.get('STATSD_PORT'):
            try:
                self.statsd_client = StatsClient(os.environ.get('STATSD_HOST'), os.environ.get('STATSD_PORT'))
            except:
                logger.info('ERROR: cannot connect to statsd host')

        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response and response.status_code > 300:
            return response

        self.process_response(request, response)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not self.statsd_client:
            return

        request.statsd_timer = self.statsd_client.timer(f'frontends.{settings.FRONTEND_NAME}.{view_func.__name__}')
        request.statsd_timer.start()

    def process_response(self, request, response):
        if not self.statsd_client:
            return

        request.statsd_timer.stop()
