"""Reloadr - Python library for hot code reloading
(c) 2015-2016 Hugo Herter
"""

import inspect
import redbaron
from baron.parser import ParsingError
import threading
import types
from time import sleep

__author__ = "Hugo Herter"
__version__ = '0.2.0'


def get_new_source(target, kind):
    """Get the new source code of the target if given kind ('class' or 'def').

    This works by using RedBaron to fetch the source code of the first object
    that shares its name and kind with the target, inside the Python file from
    which the target has been loaded.
    """
    assert kind in ('class', 'def')

    filepath = inspect.getsourcefile(target)
    red = redbaron.RedBaron(open(filepath).read())
    # dumps() returns Python code as a string
    return red.find(kind, target.__name__).dumps()


def reload_target(target, kind):
    """Get the new target class/function corresponding to the given target.

    This works by executing the new source code of the target inside the
    namespace of its module (for imports, ...), and then returning the variable
    sharing its name with the target from the new local namespace.
    """
    assert kind in ('class', 'def')

    source = get_new_source(target, kind)
    module = inspect.getmodule(target)
    # We will populate these locals using exec()
    locals_ = {}
    # module.__dict__ is the namespace of the module
    exec(source, module.__dict__, locals_)
    # The result is expected to be decorated with @reloadr, so we return
    # ._target, which corresponds to the class itself and not the Reloadr class
    return locals_[target.__name__]._target


def reload_class(target):
    "Get the new class object corresponding to the target class."
    return reload_target(target, 'class')


def reload_function(target):
    "Get the new function object corresponding to the target function."
    return reload_target(target, 'def')


class GenericReloadr:

    def _autoreload(self, interval=1):
        "Reload the target every `interval` seconds."
        while True:
            self._reload()
            sleep(interval)

    def _start_autoreload(self, interval=1):
        "Start a thread that reloads the target every `interval` seconds."
        thread = threading.Thread(target=self._autoreload)
        thread.start()


class ClassReloadr(GenericReloadr):

    def __init__(self, target):
        # target is the decorated class/function
        self._target = target
        self._instances = []  # For classes, keep a reference to all instances

    def __call__(self, *args, **kwargs):
        instance = self._target.__call__(*args, **kwargs)
        # Register a reference to the instance
        self._instances.append(instance)
        return instance

    def _reload(self):
        "Manually reload the class with its new code."
        try:
            self._target = reload_class(self._target)
            # Replace the class reference of all instances with the new class
            for instance in self._instances:
                instance.__class__ = self._target
        except ParsingError as error:
            print('ParsingError', error)


class FuncReloadr(GenericReloadr):

    def __init__(self, target):
        # target is the decorated class/function
        self._target = target

    def __call__(self, *args, **kwargs):
        "Proxy function call to the target"
        return self._target.__call__(*args, **kwargs)

    def _reload(self):
        "Manually reload the function with its new code."
        try:
            self._instance = reload_function(self._target)
        except ParsingError as error:
            print('ParsingError', error)


def reloadr(target):
    "Main decorator, forwards the target to the appropriate class."
    if isinstance(target, types.FunctionType):
        return FuncReloadr(target)
    else:
        return ClassReloadr(target)
