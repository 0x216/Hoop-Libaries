import json

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from kombu.serialization import register

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .dates import encode_datetime, encode_date, encode_time
from .text import camelcase


class ModelEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, models.QuerySet):
            return list(obj)

        if isinstance(obj, models.Model):
            fields = {}

            for field in obj._meta.get_fields():

                if field.is_relation:
                    # One to one relationships can be directly embedded
                    if field.one_to_one:
                        try:
                            fields[camelcase(field.name)] = getattr(obj, field.name)
                        except ObjectDoesNotExist:
                            fields[camelcase(field.name)] = None

                    # One to many relationships are represented as a list
                    if field.one_to_many:
                        try:
                            fields[camelcase(field.name)] = list(getattr(obj, field.name).all())
                        except AttributeError:
                            pass

                    # Many to Many relationships are represented as a list
                    if field.many_to_many:
                        try:
                            fields[camelcase(field.name)] = list(getattr(obj, field.name).all())
                        except AttributeError:
                            pass

                    # Many to one with no reverse link can also be used directly
                    elif field.many_to_one and field.rel.related_name == '+':
                        fields[camelcase(field.name)] = getattr(obj, field.name)
                else:
                    fields[camelcase(field.name)] = getattr(obj, field.name)

            return fields

        if isinstance(obj, datetime):
            return encode_datetime(obj)

        if isinstance(obj, date):
            return encode_date(obj)

        if isinstance(obj, time):
            return encode_time(obj)

        if isinstance(obj, Decimal) or isinstance(obj, UUID):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def dumps(obj):
    return json.dumps(obj, cls=ModelEncoder)


register('hoop-json', dumps, json.loads, content_type='application/json', content_encoding='utf-8')
