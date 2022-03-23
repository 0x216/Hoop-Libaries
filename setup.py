#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='hoop',
    version='0.96.14',
    description=
    'A shared library containing utility functions and classes that are commonly used from the frontends & services.',
    author='Matt Eunson',
    author_email='matt@hoop.co.uk',
    url='http://hoop.co.uk/',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'celery==3.1.17',
        'clint==0.5.1',
        'Django>=1.5',
        'django-redis-cache>=0.13.0',
        'mandrill==1.0.57',
        'PyMySQL>=0.6.6',
        'py-moneyed==0.8.0',
        'requests>=2.7.0',
        'sentry-sdk==0.14.1',
        'simplejson==3.16.0',
        'statsd>=3.2.2,<4',
    ]
)
