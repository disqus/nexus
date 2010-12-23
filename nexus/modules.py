from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import RequestContext, Context

import hashlib
import os

class NexusModule(object):
    # base url (pattern name) to show in navigation
    home_url = None
    # generic permission required
    permission = None
    media_root = None
    
    def __init__(self, site, category=None, name=None, app_name=None):
        self.category = category
        self.site = site
        self.name = name
        self.app_name = app_name
        if not self.media_root:
            mod = __import__(self.__class__.__module__)
            self.media_root = os.path.normpath(os.path.join(os.path.dirname(mod.__file__), 'media'))

    def render_to_string(self, template, context={}, request=None):
        if request:
            context_instance = RequestContext(request)
        else:
            context_instance = Context()
        
        return render_to_string(template, context,
            context_instance=context_instance
        )

    def render_to_response(self, template, context, request):
        context.update(self.get_context(request))
        return self.site.render_to_response(template, context, request, current_app=self.name)

    def as_view(self, *args, **kwargs):
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
        from django.conf.urls.defaults import patterns

        return patterns('')

    def urls(self):
        if self.app_name and self.name:
            return self.get_urls(), self.app_name, self.name
        return self.get_urls()

    urls = property(urls)

    def get_home_url(self):
        if self.app_name:
            home_url = '%s:%s' % (self.app_name, self.home_url)
        else:
            home_url = self.home_url
        return home_url

    def get_trail(self, request):
        return [
            (self.get_title(), reverse(self.get_home_url(), current_app=self.app_name)),
        ]

