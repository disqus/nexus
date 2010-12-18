from django.template.loader import render_to_string
from django.template import RequestContext, Context

class BaseNexusModule(object):
    def render_to_string(self, template, context={}, request=None):
        if request:
            context_instance = RequestContext(request)
        else:
            context_instance = Context()
        
        return render_to_string(template, context,
            context_instance=context_instance
        )

    def get_title(self):
        return self.__class__.__name__

    def get_urls(self):
        from django.conf.urls.defaults import patterns

        return patterns('')
        
class NexusModule(BaseNexusModule):
    pass