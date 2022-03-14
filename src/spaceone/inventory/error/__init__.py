import inspect, pkgutil

__all__ = []

for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    module = loader.find_module(module_name).load_module(module_name)
    if hasattr(module, '__all__'):
        for target in getattr(module, '__all__'):
            globals()[target] = getattr(module, target)
            __all__.append(target)
    else:
        for name, object in inspect.getmembers(module):
            if inspect.isclass(object) or inspect.isfunction(object):
                globals()[name] = object
                __all__.append(name)
