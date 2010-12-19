import nexus

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe

class NexusAdminSite(admin.AdminSite):
    index_template = 'nexus/admin/index.html'
    app_index_template = 'nexus/admin/app_index.html'

    # def __init__(self, name, app_name):
    #     super(NexusAdminSite, self).__init__(name, app_name)

    def has_permission(self, request):
        return self.module.site.has_permission(request)

    def get_context(self, request):
        context = self.module.get_context(request)
        context.update(self.module.site.get_context(request))
        return context

    def index(self, request, extra_context=None):
        return super(NexusAdminSite, self).index(request, self.get_context(request))

    def app_index(self, request, app_label, extra_context=None):
        return super(NexusAdminSite, self).app_index(request, app_label, self.get_context(request))

class AdminModule(nexus.NexusModule):
    home_url = 'index'

    def __init__(self, site):
        new_site = NexusAdminSite(site.name, site.app_name)
        new_site.module = self
        new_site._registry = site._registry.copy()
        for model, admin in new_site._registry.iteritems():
            self.set_templates(model, admin)
        self.admin_site = new_site
        self.app_name = new_site.app_name
        self.name = new_site.name

    def get_urls(self):
        return self.admin_site.get_urls()

    def urls(self):
        return self.admin_site.urls

    urls = property(urls)

    def set_templates(self, model, admin):
        # TODO:
        pass

    def get_title(self):
        return 'Model Admin'

    def render_on_dashboard(self, request):
        return mark_safe('<p>You have %s admin modules registered</p>' % len(self.admin_site._registry))

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    nexus.site.register(AdminModule(admin.site), 'admin')