"""
Nexus
~~~~~
"""

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('nexus').version
except Exception, e:
    VERSION = 'unknown'

# XXX: code based on django.contrib.admin auto discovery

from nexus.sites import NexusSite, site
from nexus.modules import NexusModule

__all__ = ('autodiscover', 'NexusSite', 'NexusModule', 'site')

# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
LOADING = False

def autodiscover(site=None):
    """
    Auto-discover INSTALLED_APPS nexus.py modules and fail silently when
    not present. This forces an import on them to register any api bits they
    may want.

    Specifying ``site`` will register all auto discovered modules with the new site.
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # admin.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global LOADING
    if LOADING:
        return
    LOADING = True

    if site:
        orig_site = globals()['site']
        globals()['site'] = locals()['site']

    import imp
    from django.utils.importlib import import_module
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an api.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        try:
            app_path = import_module(app).__path__
        except (AttributeError, ImportError):
            continue

        # Step 2: use imp.find_module to find the app's admin.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            imp.find_module('nexus_modules', app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        import_module("%s.nexus_modules" % app)
    # # load builtins
    # from gargoyle.builtins import *

    if site:
        globals()['site'] = orig_site

    # autodiscover was successful, reset loading flag.
    LOADING = False
