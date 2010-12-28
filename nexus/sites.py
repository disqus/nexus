# Core site concept heavily inspired by django.contrib.sites

import mimetypes
import os
import os.path
import posixpath
import stat
import urllib

from nexus.modules import NexusModule
from nexus.utils.routes import reverse, url

NEXUS_ROOT = os.path.normpath(os.path.dirname(__file__))

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
            return self.respond("Directory indexes are not allowed here.", code=404)
        if not os.path.exists(fullpath):
            return self.respond('"%s" does not exist' % fullpath, code=404)
        # Respect the If-Modified-Since header.
        statobj = os.stat(fullpath)
        mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                  statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
            return self.respond(mimetype=mimetype, code=304)
        contents = open(fullpath, 'rb').read()
        response = self.respond(contents, mimetype=mimetype)
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

