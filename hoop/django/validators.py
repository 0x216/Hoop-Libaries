import uuid

from clint.textui.validators import ValidationError

from hoop.util.dates import decode_date


def date_validator(value):
    try:
        return decode_date(value).date()
    except ValueError:
        raise ValidationError('Enter a valid date.')


def uuid_validator(value):
    try:
        return uuid.UUID(value)
    except ValueError:
        raise ValidationError('Enter a valid UUID.')
