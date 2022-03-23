from django.core.wsgi import get_wsgi_application
from os import environ

from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware

from hoop.hula import sentry

sentry.init()

environ.setdefault("DJANGO_SETTINGS_MODULE", "hoop.hula.service.settings")

application = SentryWsgiMiddleware(get_wsgi_application())
