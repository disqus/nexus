Nexus
-----

Install it::

	pip install nexus
	
Enable it::

	# settings.py
	INSTALLED_APPS = (
	    ...
	    'nexus',
	)

	import nexus
	
	nexus.autodiscover()
	
	# urls.py
	urlpatterns = patterns('',
	    ('^nexus/', include(nexus.site.urls)),
	)
