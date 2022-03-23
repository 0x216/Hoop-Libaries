from kombu import Exchange, Queue

import hoop.util.serialization

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'hoop-json'

CELERY_RESULT_BACKEND = 'rpc'

HOOP_SERVICES = [
    'admins', 'admin_sessions', 'categories', 'events', 'places', 'sessions', 'short_urls', 'users', 'emails'
]

CELERY_ACKS_LATE = False
CELERY_DISABLE_RATE_LIMITS = True

# Do we want to use transient or durable queues?
HOOP_TRANSIENT = True

CELERY_QUEUES = [
    Queue('celery', routing_key='celery'),
]

for service in HOOP_SERVICES:
    if HOOP_TRANSIENT:
        queue = Queue(service, Exchange(service, delivery_mode=1), routing_key=service, durable=False)
    else:
        queue = Queue(service, Exchange(service), routing_key=service)

    CELERY_QUEUES.append(queue)
