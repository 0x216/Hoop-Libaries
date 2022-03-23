import re

from urllib.parse import urlparse
from uuid import uuid4

from django.conf import settings
from django.utils import timezone

from hoop.hula import Hula
from hoop.util.dates import encode_datetime
from hoop.util.user_agent import is_mobile

TRACKING_COOKIE_KEY = 'hoop-sid'
TRACKING_COOKIE_MAX_AGE = 90 * 24 * 60 * 60 # 90 Days
BOOKING_REFERER_COOKIE_KEY = 'hoop-booking-referer'

# Util method for sending tracking data to Tracking Service.
# Also sets a session_id cookie on the client
def track_events(request, response, events):
    try:
        user_agent = request.META['HTTP_USER_AGENT']
    except KeyError:
        return False

    if not user_agent:
        return False

    bot_user_agent_strings = [
        'bot',
        'spider',
        'facebookexternalhit',
        'crawler',
        'sentry',
        'spaziodati',
        'mediapartners',
    ]
    bot_re = '({})'.format('|'.join(bot_user_agent_strings))
    if re.search(bot_re, user_agent, re.IGNORECASE) is not None:
        return False

    session_id = request.COOKIES.get(TRACKING_COOKIE_KEY)
    if not session_id:
        session_id = str(uuid4())

    for event in events:
        event['sessionID'] = session_id
        event['systemType'] = 'Web'
        event['deviceModel'] = 'Mobile' if is_mobile(request) else 'Desktop'
        event['extra'] = user_agent
        event['id'] = str(uuid4())
        event['date'] = encode_datetime(timezone.now())
        event['appVersion'] = settings.GIT_HASH

        if event.get('screenName') is not None:
            event['screenViewURL'] = request.get_full_path()

    Hula().execute('tracking', 'events.add', events, background=True, version='v1')

    domain = request.get_host().split(':')[0]
    response.set_cookie(TRACKING_COOKIE_KEY, session_id, max_age=TRACKING_COOKIE_MAX_AGE, domain=domain)

    return True


def set_referer_cookie(request, response):
    try:
        referer_url = request.META['HTTP_REFERER']
    except KeyError:
        return

    domain = request.get_host().split(':')[0]
    url = urlparse(referer_url)
    response.set_cookie(BOOKING_REFERER_COOKIE_KEY, url.path + ('?' + url.query if url.query else ''), domain=domain)

    return True

def get_referer_from_cookie(request):
    return request.COOKIES.get(BOOKING_REFERER_COOKIE_KEY)
