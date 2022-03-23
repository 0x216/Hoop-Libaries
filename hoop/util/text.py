import re


def camelcase(s):
    return overrides(re.sub(r'(?!^)_([a-zA-Z])', lambda m: m.group(1).upper(), s))


def underscored(s):
    return re.sub('([A-Z]+)', r'_\1', s).lower()


def overrides(s):
    overrides = {
        'Id': 'ID',
        'Url': 'URL',
    }

    for original, override in overrides.items():
        s = s.replace(original, override)

    return s


def strip_bad_characters(s):
    invisible_chars = [
        r'\u200b', # Zero width space
    ]
    pattern = r'({})'.format('|'.join(invisible_chars))
    s = re.sub(pattern, r'', s)

    return s.strip()
