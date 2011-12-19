from django import template
from django.utils.datastructures import SortedDict

import nexus
from nexus import conf
from nexus.modules import NexusModule

register = template.Library()


def nexus_media_prefix():
    return conf.MEDIA_PREFIX.rstrip('/')
register.simple_tag(nexus_media_prefix)


def nexus_version():
    return nexus.VERSION
register.simple_tag(nexus_version)


def show_navigation(context):
    site = context.get('nexus_site', NexusModule.get_global('site'))
    request = NexusModule.get_request()

    category_link_set = SortedDict([(k, {
        'label': v,
        'links': [],
    }) for k, v in site.get_categories()])

    for namespace, module in site._registry.iteritems():
        module, category = module

        if module.permission and not request.user.has_perm(module.permission):
            continue

        home_url = None
        if 'request' in context:
            home_url = module.get_home_url(context['request'])

        if not home_url:
            continue

        active = request.path.startswith(home_url)

        if category not in category_link_set:
            if category:
                label = site.get_category_label(category)
            else:
                label = None
            category_link_set[category] = {
                'label': label,
                'links': []
            }

        category_link_set[category]['links'].append((module.get_title(), home_url, active))

        category_link_set[category]['active'] = active

    return {
        'nexus_site': site,
        'category_link_set': category_link_set.itervalues(),
    }
register.inclusion_tag('nexus/navigation.html', takes_context=True)(show_navigation)
