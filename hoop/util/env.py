from os import environ


def name():
    if 'HOOP_ENV' not in environ:
        return 'loc'
    else:
        return environ['HOOP_ENV']


def name_human():
    ENVIRONMENTS = {
        'dev': 'Development',
        'stg': 'Staging',
        'prd': 'Production',
        'loc': 'Local',
    }
    return ENVIRONMENTS[name()]


def debug():
    return (name() != 'prd')
