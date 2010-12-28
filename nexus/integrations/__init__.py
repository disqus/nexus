from nexus.utils import importlib

def get_integration(name):
    module = importlib.import_module(name)
    
    return module

integration = get_integration()