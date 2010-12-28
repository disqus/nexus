from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('nexus', 'templates'))

def render_template(template, context):
    template = env.get_template(template)
    return template.render(context)