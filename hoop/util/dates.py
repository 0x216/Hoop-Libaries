import pytz

from datetime import datetime, timedelta

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
PRECISE_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'


def encode_datetime(date, precise=False):
    if date is None:
        return None

    if precise:
        return date.strftime(PRECISE_DATETIME_FORMAT)

    return date.strftime(DATETIME_FORMAT)


def decode_datetime(string, precise=False):
    try:
        if precise:
            return datetime.strptime(string, PRECISE_DATETIME_FORMAT).replace(tzinfo=pytz.UTC)

        return datetime.strptime(string, DATETIME_FORMAT).replace(tzinfo=pytz.UTC)
    except ValueError:
        try:
            return datetime.strptime(string, DATETIME_FORMAT[:-1])
        except ValueError:
            return datetime.strptime(string[:-6], DATETIME_FORMAT[:-1])


def encode_date(date):
    if date is None:
        return None

    return date.strftime(DATE_FORMAT)


def decode_date(string):
    return datetime.strptime(string, DATE_FORMAT)


def encode_time(time):
    if time is None:
        return None

    return time.strftime(TIME_FORMAT)


def decode_time(string):
    return datetime.strptime(string, TIME_FORMAT).time()


def suffixed_day(date):
    day_index = int(date.strftime('%-d'))

    if day_index in range(11, 14):
        day_suffix = 'th'
    else:
        day_suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day_index % 10, 'th')

    return date.strftime('%-d') + day_suffix


def format_date_range(start_date, end_date, include_weekday=False):
    if isinstance(start_date, datetime):
        start_date = start_date.date()

    if isinstance(end_date, datetime):
        end_date = end_date.date()

    month_start = start_date.strftime('%b')
    month_end = end_date.strftime('%b')

    day_start = suffixed_day(start_date)
    day_end = suffixed_day(end_date)

    if include_weekday:
        day_start = '%s %s' % (
            start_date.strftime('%a'),
            day_start,
        )

        day_end = '%s %s' % (
            end_date.strftime('%a'),
            day_end,
        )

    if start_date == end_date:
        return '%s %s' % (
            day_start,
            month_start,
        )

    if month_start == month_end:
        return '%s - %s %s' % (
            day_start,
            day_end,
            month_start,
        )

    return '%s %s - %s %s' % (
        day_start,
        month_start,
        day_end,
        month_end,
    )


def decode_localised_date(date):
    try:
        return decode_datetime(date).astimezone(pytz.timezone('Europe/London'))

    except ValueError:
        return decode_date(date)


def format_time(start_time, end_time, tz_output=None):
    if isinstance(start_time, str):
        start_time = decode_localised_date(start_time)

    if isinstance(end_time, str):
        end_time = decode_localised_date(end_time)

    if tz_output:
        tz_output = get_timezone(tz_output)

        start_time = start_time.astimezone(tz_output)

        if end_time:
            end_time = end_time.astimezone(tz_output)

    # Check this is actually a time range
    if start_time == end_time:
        end_time = None

    formatted_time = start_time.strftime('%-I:%M%p').lower()

    if end_time:
        formatted_time += ' – %s' % end_time.strftime('%-I:%M%p').lower()

    return formatted_time


def get_timezone(timezone):
    if isinstance(timezone, str):
        timezone = pytz.timezone(timezone)

    return timezone


def combine_datetime(date, time, tz_input=None, tz_output=None):
    if isinstance(date, str):
        date = decode_date(date).date()

    if isinstance(time, str):
        time = decode_time(time)

    combined = datetime.combine(date, time)

    if tz_input:
        combined = get_timezone(tz_input).localize(combined)

    if tz_output:
        combined = combined.astimezone(get_timezone(tz_output))

    return combined


def get_date_list(start_date, end_date, inclusive=True):
    days = (end_date - start_date).days

    if inclusive:
        days += 1

    return [start_date + timedelta(days=i) for i in range(days)]


def check_date_range(date, start_date, end_date):
    if isinstance(date, str):
        date = decode_date(date).date()

    if isinstance(start_date, str):
        start_date = decode_date(start_date).date()

    if isinstance(end_date, str):
        end_date = decode_date(end_date).date()

    if date < start_date:
        return False

    if date > end_date:
        return False

    return True
