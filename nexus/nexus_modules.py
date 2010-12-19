import nexus

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe

def make_nexus_model_admin(model_admin):
    class NexusModelAdmin(model_admin.__class__):
        def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
            opts = self.model._meta
            app_label = opts.app_label

            self.change_form_template = (
                'nexus/admin/%s/%s/change_form.html' % (app_label, opts.object_name.lower()),
                'nexus/admin/%s/change_form.html' % app_label,
                'nexus/admin/change_form.html',
            )

            extra_context = self.admin_site.get_context(request)
            del extra_context['title']

            context.update(extra_context)
            return super(NexusModelAdmin, self).render_change_form(request, context, add, change, form_url, obj)

        def changelist_view(self, request, extra_context=None):
            opts = self.model._meta
            app_label = opts.app_label
            
            self.change_list_template = (
                'nexus/admin/%s/%s/change_list.html' % (app_label, opts.object_name.lower()),
                'nexus/admin/%s/change_list.html' % app_label,
                'nexus/admin/change_list.html'
            )

            if not extra_context:
                extra_context = self.admin_site.get_context(request)
            else:
                extra_context.update(self.admin_site.get_context(request))
            
            del extra_context['title']
            return super(NexusModelAdmin, self).changelist_view(request, extra_context)
    return NexusModelAdmin

def make_nexus_admin_site(admin_site):
    class NexusAdminSite(admin_site.__class__):
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
    return NexusAdminSite

class AdminModule(nexus.NexusModule):
    home_url = 'index'

    def __init__(self, site):
        new_site = make_nexus_admin_site(site)(site.name, site.app_name)
        new_site.module = self
        for model, admin in site._registry.iteritems():
            new_site.register(model, make_nexus_model_admin(admin))
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