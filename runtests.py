#!/usr/bin/env python
import sys
from os.path import dirname, abspath

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        # HACK: this fixes our threaded runserver remote tests
        # TEST_DATABASE_NAME='test_sentry',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django.contrib.sites',

            # Included to fix Disqus' test Django which solves IntegrityMessage case
            'django.contrib.contenttypes',
            'nexus',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
    )


from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=2, interactive=True)


# from south.management.commands import patch_for_test_db_setup
# patch_for_test_db_setup()

def runtests(*test_args):
    if not test_args:
        test_args = ['nexus']

    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(failures)

if __name__ == '__main__':
    runtests(*sys.argv[1:])
