"""Reloadr - Python library for hot code reloading
(c) 2015 Hugo Herter
"""

import inspect
import redbaron


def get_new_source(target):
    filepath = inspect.getsourcefile(target)
    red = redbaron.RedBaron(open(filepath).read())
    return red.find('class', target.__name__).dumps()


def reload_class(target):
    source = get_new_source(target)
    module = inspect.getmodule(target)
    locals_ = {}
    exec(source, module.__dict__, locals_)
    return locals_[target.__name__]._target


class Reloadr:
    def __init__(self, target):
        self._target = target
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._init_args = args
            self._init_kwargs = kwargs
            self._instance = self._target.__call__(*args, **kwargs)
            return self._instance
        else:
            return self._instance.__call__(*args, **kwargs)

    def _reload(self):
        self._target = reload_class(self._target)
        self._instance.__class__ = self._target


reloadr = Reloadr
