from django.conf.urls.defaults import patterns, include, url

import nexus

nexus.autodiscover()

urlpatterns = patterns('',
    url(r'gargoyle/', include('gargoyle.urls')),
    url(r'', include(nexus.site.urls)),
)
