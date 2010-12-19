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
        return self.site.has_permission(request)
    

class AdminModule(nexus.NexusModule):
    def __init__(self, site):
        new_site = NexusAdminSite(site.name, site.app_name)
        new_site.site = self
        new_site._registry = site._registry.copy()
        for model, admin in new_site._registry.iteritems():
            self.set_templates(model, admin)
        self.admin_site = new_site

    def set_templates(self, model, admin):
        # TODO:
        pass

    def get_title(self):
        return 'Model Admin'

    def render_on_dashboard(self, request):
        return mark_safe('<p>You have %s admin modules registered</p>' % len(self.admin_site._registry))

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    nexus.site.register(AdminModule(admin.site))