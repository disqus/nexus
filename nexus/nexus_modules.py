import nexus

from django.conf import settings
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _

class NexusAdminSite(admin.AdminSite):
    index_template = 'nexus/admin/index.html'
    app_index_template = 'nexus/admin/app_index.html'

    # def __init__(self, name, app_name):
    #     super(NexusAdminSite, self).__init__(name, app_name)

    def has_permission(self, request):
        return self.module.site.has_permission(request)

    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                        'perms': perms,
                    }
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_url': app_label + '/',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(lambda x, y: cmp(x['name'], y['name']))

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(lambda x, y: cmp(x['name'], y['name']))

        context = {
            'title': _('Site administration'),
            'app_list': app_list,
            'root_path': self.root_path,
        }
        context.update(extra_context or {})
        return self.module.render_to_response('nexus/admin/index.html', context, request)

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