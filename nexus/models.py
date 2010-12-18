from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_reqs = ('django.contrib.auth', 'django.contrib.sessions')
for r in _reqs:
    if r not in settings.INSTALLED_APPS:
        raise ImproperlyConfigured("Put '%s' in your "
            "INSTALLED_APPS setting in order to use the nexus application." % r)

