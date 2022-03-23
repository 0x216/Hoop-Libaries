import os

import sentry_sdk

from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

from hoop.util import env


def init(**kwargs):
    if not os.environ.get('SENTRY_DSN'):
        return

    sentry_sdk.init(
        os.environ['SENTRY_DSN'],
        environment=env.name(),
        integrations=[CeleryIntegration(), DjangoIntegration()],
    )
