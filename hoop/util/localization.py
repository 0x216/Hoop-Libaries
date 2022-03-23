import os

from django.conf import settings

from moneyed import Money, GBP, USD
from moneyed.localization import format_money as _format_money

from hoop.util import env


def get_locale():
    return settings.LOCALE


def get_currency():
    return settings.CURRENCY


def format_money(value):
    currency = get_currency()
    money = Money(value, currency)

    locale = get_locale()
    formatted = _format_money(money, locale=locale)

    return formatted


def get_localization_settings():
    try:
        CURRENCY = {
            'us': USD,
        }[env.name()]
    except KeyError:
        CURRENCY = GBP

    try:
        LOCALE = os.environ['LOCALE']
    except KeyError:
        LOCALE = 'en_GB'

    return CURRENCY, LOCALE
