from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.template import RequestContext, Context

class NexusModule(object):
    home_url = None

    def render_to_string(self, template, context={}, request=None):
        if request:
            context_instance = RequestContext(request)
        else:
            context_instance = Context()
        
        return render_to_string(template, context,
            context_instance=context_instance
        )
    
    def render_to_response(self, template, context={}, request=None):
        context.update({
            'title': self.get_title(),
            'trail_bits': self.get_trail(request),
        })
        return self.site.render_to_response(template, context, request)

    def as_view(self, *args, **kwargs):
        return self.site.as_view(*args, **kwargs)
    
    def get_title(self):
        return self.__class__.__name__

    def get_dashboard_title(self):
        return self.get_title()

    def get_urls(self):
        from django.conf.urls.defaults import patterns

        return patterns('')

    def get_trail(self, request):
        return [
            (self.get_title(), reverse(self.home_url)),
        ]

