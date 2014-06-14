from django.core.urlresolvers import reverse
from django.http import HttpRequest

import hashlib
import inspect
import logging
import os

# import thread lib from py3k or 2
try:
    import _thread as thread
except ImportError:
    import thread


class NexusModule(object):
    # base url (pattern name) to show in navigation
    home_url = None

    # generic permission required
    permission = None

    media_root = None

    logger_name = None

    # list of active sites within process
    _globals = {}

    def __init__(self, site, category=None, name=None, app_name=None):
        self.category = category
        self.site = site
        self.name = name
        self.app_name = app_name

        # Set up default logging for this module
        if not self.logger_name:
            self.logger_name = 'nexus.%s' % (self.name)
        self.logger = logging.getLogger(self.logger_name)

        if not self.media_root:
            mod = __import__(self.__class__.__module__)
            self.media_root = os.path.normpath(os.path.join(os.path.dirname(mod.__file__), 'media'))

    def __getattribute__(self, name):
        NexusModule.set_global('site', object.__getattribute__(self, 'site'))
        return object.__getattribute__(self, name)

    @classmethod
    def set_global(cls, key, value):
        ident = thread.get_ident()
        if ident not in cls._globals:
            cls._globals[ident] = {}
        cls._globals[ident][key] = value

    @classmethod
    def get_global(cls, key):
        return cls._globals.get(thread.get_ident(), {}).get(key)

    @classmethod
    def get_request(cls):
        """
        Get the HTTPRequest object from thread storage or from a callee by searching
        each frame in the call stack.
        """
        request = cls.get_global('request')
        if request:
            return request
        try:
            stack = inspect.stack()
        except IndexError:
            # in some cases this may return an index error
            # (pyc files dont match py files for example)
            return
        for frame, _, _, _, _, _ in stack:
            if 'request' in frame.f_locals:
                if isinstance(frame.f_locals['request'], HttpRequest):
                    request = frame.f_locals['request']
                    cls.set_global('request', request)
                    return request

    def render_to_string(self, template, context={}, request=None):
        context.update(self.get_context(request))
        return self.site.render_to_string(template, context, request, current_app=self.name)

    def render_to_response(self, template, context={}, request=None):
        context.update(self.get_context(request))
        return self.site.render_to_response(template, context, request, current_app=self.name)

    def as_view(self, *args, **kwargs):
        if 'extra_permission' not in kwargs:
            kwargs['extra_permission'] = self.permission
        return self.site.as_view(*args, **kwargs)

    def get_context(self, request):
        title = self.get_title()
        return {
            'title': title,
            'module_title': title,
            'trail_bits': self.get_trail(request),
        }

    def get_namespace(self):
        return hashlib.md5(self.__class__.__module__ + '.' + self.__class__.__name__).hexdigest()

    def get_title(self):
        return self.__class__.__name__

    def get_dashboard_title(self):
        return self.get_title()

    def get_urls(self):
        try:
            from django.conf.urls import patterns
        except ImportError:  # Django<=1.4
            from django.conf.urls.defaults import patterns

        return patterns('')

    def urls(self):
        if self.app_name and self.name:
            return self.get_urls(), self.app_name, self.name
        return self.get_urls()

    urls = property(urls)


    def get_trail(self, request):
        return [
            (self.get_title(), self.get_home_url(request)),
        ]

    def get_home_url(self, request):
        if self.home_url:
            if self.app_name:
                home_url_name = '%s:%s' % (self.app_name, self.home_url)
            else:
                home_url_name = self.home_url

            home_url = reverse(home_url_name, current_app=self.name)
        else:
            home_url = None

        return home_url


