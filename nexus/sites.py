# Core site concept heavily inspired by django.contrib.sites

from __future__ import absolute_import

# from django.core.urlresolvers import reverse
# from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotModified, Http404
# from django.utils.datastructures import SortedDict
# from django.utils.functional import update_wrapper
# from django.utils.http import http_date
# from django.views.decorators.cache import never_cache
# from django.views.static import was_modified_since

from nexus import app
from nexus.utils.routes import include, url, reverse, RouteInclusion
from nexus.utils.template import render_template

import hashlib
import mimetypes
import os
import os.path
import posixpath
import stat
import urllib

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

# Currently Nexus does not support multiple sites

# TODO: NexusSite should inherit from NexusModule to provide recursion on application namespaces,
# url patterns, etc. etc.
# XXX: should submodules contain dashboard behavior?

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
        self._routes = None
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
        for module in self.get_modules():
            routes.append(
                include(module.urls),
            )
    
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
        if not cacheable:
            inner = never_cache(inner)

        return update_wrapper(inner, view)

    def get_context(self, request):
        context = {
            'request': request,
            'nexus_site': self,
            'nexus_media_prefix': conf.MEDIA_PREFIX.rstrip('/'),
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
            app_name '%s:%s' % (self.parent.get_app_name(), self.parent.name)
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

    def redirect(self, path, code=302):
        return app.redirect(path, code=code)

    def render_to_response(self, template, context, request, current_app=None):
        "Shortcut for rendering to response and default context instances"
        if not current_app:
            current_app = self.name
        else:
            current_app = '%s:%s' % (self.name, current_app)
        
        context.update(self.get_context(request))
        
        template = render_template(template, context)
        
        return respond(template)

class NexusSite(NexusModule):
    def get_urls(self):
        return [
            url('/', self.as_view(self.dashboard), 'index'),
            url('/login/', self.login, 'login'),
            url('/logout/', self.as_view(self.logout), 'logout'),
            url('/media/<module>/<path>', self.media, 'media'),
        ]
        
    ## Our views
    
    def media(self, request, module, path):
        """
        Serve static files below a given point in the directory structure.
        """
        if module == 'nexus':
            document_root = os.path.join(NEXUS_ROOT, 'media')
        else:
            document_root = self.get_module(module).media_root
        
        path = posixpath.normpath(urllib.unquote(path))
        path = path.lstrip('/')
        newpath = ''
        for part in path.split('/'):
            if not part:
                # Strip empty path components.
                continue
            drive, part = os.path.splitdrive(part)
            head, part = os.path.split(part)
            if part in (os.curdir, os.pardir):
                # Strip '.' and '..' in path.
                continue
            newpath = os.path.join(newpath, part).replace('\\', '/')
        if newpath and path != newpath:
            return self.redirect(newpath)
        fullpath = os.path.join(document_root, newpath)
        if os.path.isdir(fullpath):
            raise Http404("Directory indexes are not allowed here.")
        if not os.path.exists(fullpath):
            raise Http404('"%s" does not exist' % fullpath)
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                  statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
            return HttpResponseNotModified(mimetype=mimetype)
        contents = open(fullpath, 'rb').read()
        response = HttpResponse(contents, mimetype=mimetype)
        response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
        response["Content-Length"] = len(contents)
        return response        

    def login(self, request):
        "Login form"
        from django.contrib.auth import login as login_
        from django.contrib.auth.forms import AuthenticationForm

        if request.POST:
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                login_(request, form.get_user())
                return self.redirect(request.POST.get('next') or reverse('nexus:index', current_app=self.name))
            else:
                request.session.set_test_cookie()
        else:
            form = AuthenticationForm(request)
            request.session.set_test_cookie()

        return self.render_to_response('nexus/login.html', {
            'form': form,
        }, request)
    login = never_cache(login)
    
    def logout(self, request):
        "Logs out user and redirects them to Nexus home"
        from django.contrib.auth import logout

        logout(request)

        return self.redirect(reverse('nexus:index', current_app=self.name))

    def dashboard(self, request):
        "Basic dashboard panel"
        # TODO: these should be ajax
        module_set = []
        for namespace, module in self.get_modules():
            if module.home_url:
                home_url = reverse(module.get_home_url(), current_app=self.name)
            else:
                home_url = None

            if hasattr(module, 'render_on_dashboard'):
                module_set.append((module.get_dashboard_title(), module.render_on_dashboard(request), home_url))
        
        return self.render_to_response('nexus/dashboard.html', {
            'module_set': module_set,
        }, request)

# setup the default site
site = NexusSite('nexus', 'nexus')

