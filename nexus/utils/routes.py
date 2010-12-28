from flask import url_for

class RouteInclusion(object):
    def __init__(self, route_set):
        self.route_set = route_set

def include(route_set):
    return RouteInclusion(route_set)

def url(path, view, name, module_name, app_name):
    return (path, view, name, module_name, app_name)

def reverse(name, current_app):
    return url_for('%s:%s' % (current_app, name))