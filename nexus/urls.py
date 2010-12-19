import os

from django.conf.urls.defaults import *

import nexus

nexus.autodiscover()

NEXUS_ROOT = os.path.dirname(__file__)

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(NEXUS_ROOT, 'media'),
        'show_indexes': True,
    }),

    url(r'^$', 'nexus.views.dashboard', name='nexus'),
)