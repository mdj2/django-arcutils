#!/usr/bin/env python
import sys

import django
from django.conf import settings

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF='urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'arcutils',
    ),
    MIDDLEWARE_CLASSES=[],
    LDAP={
        "default": {
            "host": "ldap://ldap-login.oit.pdx.edu",
            "username": "",
            "password": "",
            "search_dn": "ou=people,dc=pdx,dc=edu",
        }
    },
    LOGGING_CONFIG='arcutils.logging.basic',
)

if django.VERSION[:2] >= (1, 7):
    from django import setup
else:
    setup = lambda: None

from django.test.runner import DiscoverRunner
from django.test.utils import setup_test_environment

setup()
setup_test_environment()
test_runner = DiscoverRunner(verbosity=1)

# Django 1.6 doesn't have the app loader, so you have to manually call ready()
if django.VERSION[:2] < (1, 7):
    from arcutils.apps import ARCUtilsConfig
    ARCUtilsConfig().ready()

failures = test_runner.run_tests(['arcutils', ])
if failures:
    sys.exit(failures)
