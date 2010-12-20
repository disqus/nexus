Nexus
-----

Nexus is a pluggable admin application in Django. It's designed to give you a simple design and architecture for building admin applications.

(This project is still under active development)

Screenshot
==========

.. image:: http://dl.dropbox.com/u/116385/nexus.png

Install
=======

Install it with pip (or easy_install)::

	pip install nexus
	
Config
======

You'll need to enable it much like you would ``django.contrib.admin``.

First, add it to your ``INSTALLED_APPS`` setting::

	INSTALLED_APPS = (
	    ...
	    'nexus',
	)

Now you'll want to include it within your ``urls.py``::

	import nexus
	
	# sets up the default nexus site by detecting all nexus_modules.py files
	nexus.autodiscover()
	
	# urls.py
	urlpatterns = patterns('',
	    ('^nexus/', include(nexus.site.urls)),
	)

Modules
=======

Nexus by default includes a module that will automatically pick up ``django.contrib.admin``.

Other applications which provide Nexus modules:

* `Gargoyle <https://github.com/disqus/gargoyle>`_

(docs on writing modules coming soon)
