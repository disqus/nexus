import nexus

class HelloWorldModule(nexus.NexusModule):
    home_url = 'index'
    name = 'hello-world'

    def get_title(self):
        return 'Hello World'

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        urlpatterns = patterns('',
            url(r'^$', self.as_view(self.index), name='index'),
        )

        return urlpatterns

    def render_on_dashboard(self, request):
        return self.render_to_string('nexus/example/dashboard.html', {
            'title': 'Hello World',
        })

    def index(self, request):
        return self.render_to_response("nexus/example/index.html", {
            'title': 'Hello World',
        }, request)
nexus.site.register(HelloWorldModule, 'hello-world')
# optionally you may specify a category
# nexus.site.register(HelloWorldModule, 'hello-world', category='cache')