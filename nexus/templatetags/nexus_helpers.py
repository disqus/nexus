from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def show_navigation(context):
    site = context['nexus_site']
    request = context['request']
    
    link_set = []
    for module in site._registry.itervalues():
        if not module.home_url:
            continue

        home_url = reverse(module.get_home_url(), current_app=module.name)

        active = request.path.startswith(home_url)

        link_set.append((module.get_title(), home_url, active))

    return {
        'link_set': link_set,
    }

register.inclusion_tag('nexus/navigation.html', takes_context=True)(show_navigation)