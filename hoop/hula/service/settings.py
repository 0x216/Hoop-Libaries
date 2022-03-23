import sys

from os import environ

from hoop.util import env

DEBUG = env.debug()

DB_CHARSET = None
DB_STRICT = False

# Detect test environment
TEST_ENVIRONMENT = len(sys.argv) > 1 and sys.argv[1] == 'test'

# Import service settings
try:
    from settings import *
except ModuleNotFoundError:
    SECRET_KEY = 'TESTS'
    SERVICE_APPS = ()

# Application definition

INSTALLED_APPS = () + SERVICE_APPS

MIDDLEWARE_CLASSES = []

# Cache

if 'REDIS_PORT' in environ:
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': '%s:%s' % (environ['REDIS_PORT_6379_TCP_ADDR'], environ['REDIS_PORT_6379_TCP_PORT']),
        }
    }

# Database

import pymysql

pymysql.install_as_MySQLdb()

if 'MYSQL_HOST' in environ:
    DB_ENGINE = 'mysql'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': environ['MYSQL_HOST'],
            'PORT': environ.get('MYSQL_PORT', '3306'),
            'USER': environ['MYSQL_USER'],
            'PASSWORD': environ['MYSQL_PASS'],
            'NAME': environ['MYSQL_DB'],
            'OPTIONS': {},
        },
    }

    if not TEST_ENVIRONMENT:
        DATABASES['replica'] = {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': environ.get('REPLICA_HOST', environ['MYSQL_HOST']),
            'PORT': environ.get('MYSQL_PORT', '3306'),
            'USER': environ['MYSQL_USER'],
            'PASSWORD': environ['MYSQL_PASS'],
            'NAME': environ['MYSQL_DB'],
            'OPTIONS': {},
        }

    for db in DATABASES:
        if DB_CHARSET:
            DATABASES[db]['OPTIONS']['charset'] = DB_CHARSET

        if DB_STRICT:
            DATABASES[db]['OPTIONS']['init_command'] = "SET sql_mode='STRICT_ALL_TABLES'"

else:
    DB_ENGINE = 'sqlite'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/service.sqlite3',
        },
    }

    if not TEST_ENVIRONMENT:
        DATABASES['replica'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/replica.sqlite3',
        }

# Internationalization

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True
