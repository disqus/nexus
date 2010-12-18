import nexus

from django.contrib import admin
from django.utils.safestring import mark_safe

class AdminModule(nexus.NexusModule):
    def __init__(self, admin_site):
        self.admin_site = admin_site
    
    def get_title(self):
        return 'Model Admin'
    
    def render_on_dashboard(self, request):
        return mark_safe('<p>You have %s admin modules registered</p>' % len(self.admin_site._registry))

nexus.site.register(AdminModule(admin.site))
