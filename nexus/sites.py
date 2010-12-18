from django.shortcuts import render_to_response
from django.template import RequestContext, Context

import os

NEXUS_ROOT = os.path.dirname(__file__)

class NexusSite(object):
    _registry = set()

    def register(self, module):
        if callable(module):
            module = module()
        module.site = self
        self._registry.add(module)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': os.path.join(NEXUS_ROOT, 'media'),
                'show_indexes': True,
            }, name='nexus-media'),

            url(r'^$', self.dashboard, name='nexus'),
        )
        for module in self._registry:
            urlpatterns += module.get_urls()
        
        return urlpatterns

    urls = property(get_urls)

    def render_to_response(self, template, context={}, request=None):
        if request:
            context_instance = RequestContext(request)
        else:
            context_instance = Context()
        
        return render_to_response(template, context,
            context_instance=context_instance
        )

    def dashboard(self, request):
        # TODO: these should be ajax
        modules = []
        for module in self._registry:
            if hasattr(module, 'render_on_dashboard'):
                modules.append((module.get_title(), module.render_on_dashboard(request)))
        
        return self.render_to_response('nexus/dashboard.html', {
            'modules': modules,
        }, request)
        
    
    def __call__(self, request, path):
        if not request.user.is_staff:
            # show login pane
            pass
        return

# setup the default site

site = NexusSite()

