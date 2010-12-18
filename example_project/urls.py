from django.conf.urls.defaults import patterns, include, url

import nexus

nexus.autodiscover()

urlpatterns = patterns('',
    url(r'', include(nexus.site.urls)),
)
