import nexus

from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def make_nexus_model_admin(model_admin):
    class NexusModelAdmin(model_admin.__class__):
        delete_selected_confirmation_template = 'nexus/admin/delete_selected_confirmation.html'

        def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
            opts = self.model._meta
            app_label = opts.app_label

            self.add_form_template = self.change_form_template = (
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

        def delete_view(self, request, object_id, extra_context=None):
            opts = self.model._meta
            app_label = opts.app_label
            
            self.delete_confirmation_template = (
                'nexus/admin/%s/%s/delete_confirmation.html' % (app_label, opts.object_name.lower()),
                'nexus/admin/%s/delete_confirmation.html' % app_label,
                'nexus/admin/delete_confirmation.html'
            )

            if not extra_context:
                extra_context = self.admin_site.get_context(request)
            else:
                extra_context.update(self.admin_site.get_context(request))
            
            del extra_context['title']
            return super(NexusModelAdmin, self).delete_view(request, object_id, extra_context)

        def history_view(self, request, object_id, extra_context=None):
            opts = self.model._meta
            app_label = opts.app_label
            
            self.object_history_template = (
                'nexus/admin/%s/%s/object_history.html' % (app_label, opts.object_name.lower()),
                'nexus/admin/%s/object_history.html' % app_label,
                'nexus/admin/object_history.html'
            )

            if not extra_context:
                extra_context = self.admin_site.get_context(request)
            else:
                extra_context.update(self.admin_site.get_context(request))
            
            del extra_context['title']
            return super(NexusModelAdmin, self).history_view(request, object_id, extra_context)
    return NexusModelAdmin

def make_nexus_admin_site(admin_site):
    class NexusAdminSite(admin_site.__class__):
        index_template = 'nexus/admin/index.html'
        app_index_template = None
        password_change_template = 'nexus/admin/password_change_form.html'
        password_change_done_template = 'nexus/admin/password_change_done.html'
        
        def has_permission(self, request):
            return self.module.site.has_permission(request)

        def get_context(self, request):
            context = self.module.get_context(request)
            context.update(self.module.site.get_context(request))
            return context

        def index(self, request, extra_context=None):
            return super(NexusAdminSite, self).index(request, self.get_context(request))

        def app_index(self, request, app_label, extra_context=None):
            self.app_index_template = (
               'nexus/admin/%s/app_index.html' % app_label,
               'nexus/admin/app_index.html'
            )
            return super(NexusAdminSite, self).app_index(request, app_label, self.get_context(request))

        def password_change(self, request):
            from django.contrib.auth.forms import PasswordChangeForm
            if self.root_path is not None:
                post_change_redirect = '%spassword_change/done/' % self.root_path
            else:
                post_change_redirect = reverse('admin:password_change_done', current_app=self.name)

            if request.method == "POST":
                form = PasswordChangeForm(user=request.user, data=request.POST)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(post_change_redirect)
            else:
                form = PasswordChangeForm(user=request.user)

            return self.module.render_to_response(self.password_change_template, {
                'form': form,
            }, request)

        def password_change_done(self, request):
            return self.module.render_to_response(self.password_change_done_template, {}, request)
    return NexusAdminSite


def make_admin_module(admin_site, name=None, app_name='admin'):
    # XXX: might be a better API so we dont need to do this?
    new_site = make_nexus_admin_site(admin_site)(name, app_name)
    for model, admin in admin_site._registry.iteritems():
        new_site.register(model, make_nexus_model_admin(admin))

    class AdminModule(nexus.NexusModule):
        home_url = 'index'
        admin_site = new_site

        def __init__(self, *args, **kwargs):
            super(AdminModule, self).__init__(*args, **kwargs)
            self.app_name = new_site.app_name
            self.name = new_site.name
            new_site.module = self
            # new_site.name = self.site.name

        def get_urls(self):
            return self.admin_site.get_urls()

        def urls(self):
            return self.admin_site.urls[0], self.app_name, self.name

        urls = property(urls)

        def get_title(self):
            return 'Model Admin'

        def render_on_dashboard(self, request):
            return self.render_to_string('nexus/admin/dashboard/index.html', {
                'base_url': './' + self.app_name + '/'
            }, request)
    return AdminModule

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    nexus.site.register(make_admin_module(admin.site, admin.site.name, admin.site.app_name), admin.site.app_name)