from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import RequestContext, Context

class NexusModule(object):
    home_url = None
    
    def __init__(self, name=None, app_name=None):
        if name:
            self.name = name
        self.app_name = app_name

    def render_to_string(self, template, context={}, request=None):
        if request:
            context_instance = RequestContext(request)
        else:
            context_instance = Context()
        
        return render_to_string(template, context,
            context_instance=context_instance
        )

    def get_context(self, request):
        return {
            'title': self.get_title(),
            'trail_bits': self.get_trail(request),
        }
    
    def render_to_response(self, template, context, request):
        context.update(self.get_context(request))
        return self.site.render_to_response(template, context, request, current_app=self.app_name)

    def as_view(self, *args, **kwargs):
        return self.site.as_view(*args, **kwargs)
    
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
            (self.get_title(), reverse('%s:%s' % (self.site.name, self.get_home_url()))),
        ]

