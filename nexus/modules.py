# Core site concept heavily inspired by django.contrib.sites

from __future__ import absolute_import
# from django.utils.datastructures import SortedDict
# from django.utils.functional import update_wrapper
# from django.utils.http import http_date
# from django.views.decorators.cache import never_cache
# from django.views.static import was_modified_since

from flask import render_template, make_response
from functools import wraps

from nexus import app
from nexus.utils.routes import include, reverse, RouteInclusion

import hashlib
import os.path

NEXUS_ROOT = os.path.normpath(os.path.dirname(__file__))

def get_routes(route_set):
    for routes, module_name, app_name in route_set:
        for route_data in routes:
            if isinstance(route_data, RouteInclusion):
                for path, view, name in get_routes(route_data):
                    path = '/%s/%s' % (app_name, path)
                    name = '%s:%s' % (app_name, module_name, name)
                    yield path, view, name
            else:
                path, view, name = route_data
                path = '/%s/%s' % (app_name, path)
                name = '%s:%s' % (app_name, module_name, name)
                yield path, view, name

class NexusModule(object):
    # base url (pattern name) to show in navigation
    home_url = None
    # generic permission required
    permission = None
    # filesystem root location of media -- defaults to MODULE/media/
    media_root = None

    @classmethod
    def get_namespace(self):
        return hashlib.md5(self.__class__.__module__ + '.' + self.__class__.__name__).hexdigest()

    def __init__(self, name, app_name, parent=None):
        self._registry = {}
        #self._categories = SortedDict()
        self.name = name
        self.app_name = app_name
        self.parent = parent
        if not self.media_root:
            this = __import__(self.__class__.__module__)
            self.media_root = os.path.normpath(os.path.join(os.path.dirname(this.__file__), 'media'))
        
    def register_category(self, category, label, index=None):
        if index:
            self._categories.insert(index, category, label)
        else:
            self._categories[category] = label

    def register(self, module, name=None, app_name=None, category=None):
        if not name:
            name = module.get_namespace()
        if not app_name:
            app_name = name
        if app_name in self._registry:
            raise ValueError('%s is already registered as %r' % (app_name, self._registry[app_name][0]))
        module = module(self, name, app_name)
        self._registry[app_name] = (module, category)
        return module

    def get_urls(self):
        routes = []
        for module in self.get_modules():
            routes.append(include(module.urls))
        return routes
    
    def urls(self):
        return self.get_urls(), self.name, self.app_name

    urls = property(urls)

    def setup_routes(self):
        for path, view, name in get_routes(self.urls):
            app.add_url_rule(path, name, view_func=view)

    def has_permission(self, request):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active and request.user.is_staff

    def as_view(self, view, cacheable=False):
        "Wraps a view in authentication/caching logic"
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                # show login pane
                return self.login(request, *args, **kwargs)
            return view(request, *args, **kwargs)
        # Mark it as never_cache
        # TODO:
        # if not cacheable:
        #     inner = never_cache(inner)
        return wraps(view)(inner)

    def get_context(self, request):
        context = {
            'request': request,
            'nexus_site': self,
            'nexus_media_prefix': app.config['MEDIA_PREFIX'].rstrip('/'),
        }
        return context

    def get_modules(self):
        for module, category in self._registry.itervalues():
            yield module
    
    def get_module(self, module):
        return self._registry[module][0]

    def get_categories(self):
        for k, v in self._categories.iteritems():
            yield k, v

    def get_category_label(self, category):
        return self._categories.get(category, category.title().replace('_', ' '))

    def get_title(self):
        return self.__class__.__name__

    def get_dashboard_title(self):
        return self.get_title()

    def get_home_url(self):
        return '%s:%s' % (self.app_name, self.home_url)

    def get_app_name(self):
        if self.parent:
            app_name = '%s:%s' % (self.parent.get_app_name(), self.parent.name)
        else:
            app_name = ''
        return self.app_name

    def get_trail(self, request):
        if self.parent:
            trail = self.parent.get_trail()
        else:
            trail = []

        trail.append((self.get_title(), reverse(self.get_home_url(), current_app=self.get_app_name())))

        return trail

    # Helper methods for HTTP

    def respond(self, content='', code=200, mimetype='text/html'):
        response = make_response(content, code)
        response['Content-Type'] = mimetype
        return response

    def render(self, template, context):
        return render_template(template, context)

    def redirect(self, path, code=302):
        return app.redirect(path, code=code)

    # TODO: kill this?
    def render_to_response(self, template, context, request, current_app=None):
        "Shortcut for rendering to response and default context instances"
        if not current_app:
            current_app = self.name
        else:
            current_app = '%s:%s' % (self.name, current_app)
        
        context.update(self.get_context(request))
        
        return render_template(template, context)