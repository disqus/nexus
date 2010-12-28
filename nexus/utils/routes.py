from flask import url_for

# TODO: refactor this so iter can happen in RouteInclusion as well as a RouteSet
def get_routes(route_set):
    for routes, module_name, app_name in route_set:
        for route_data in routes:
            if isinstance(route_data, RouteInclusion):
                for path, view, name in get_routes(route_data):
                    path = '/'.join([app_name, path])
                    name = ':'.join([app_name, module_name, name])
                    yield path, view, name
            else:
                path, view, name = route_data
                path = '/'.join([app_name, path])
                name = ':'.join([app_name, module_name, name])
                yield path, view, name


class RouteInclusion(object):
    def __init__(self, route_set):
        self.route_set = route_set

def include(route_set):
    return RouteInclusion(route_set)

def url(path, view, name):
    return (path, view, name)

def reverse(name, current_app):
    return url_for('%s:%s' % (current_app, name))