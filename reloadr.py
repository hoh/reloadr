"""Reloadr - Python library for hot code reloading
(c) 2015-2017 Hugo Herter
"""

from os.path import dirname
import inspect
import redbaron
from baron.parser import ParsingError
import threading
import types
from time import sleep
import weakref

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

__author__ = "Hugo Herter"
__version__ = '0.3.0'


def get_new_source(target, kind, filepath=None):
    """Get the new source code of the target if given kind ('class' or 'def').

    This works by using RedBaron to fetch the source code of the first object
    that shares its name and kind with the target, inside the Python file from
    which the target has been loaded.
    """
    assert kind in ('class', 'def')

    filepath = filepath or inspect.getsourcefile(target)
    red = redbaron.RedBaron(open(filepath).read())
    # dumps() returns Python code as a string
    return red.find(kind, target.__name__).dumps()


def reload_target(target, kind, filepath=None):
    """Get the new target class/function corresponding to the given target.

    This works by executing the new source code of the target inside the
    namespace of its module (for imports, ...), and then returning the variable
    sharing its name with the target from the new local namespace.
    """
    assert kind in ('class', 'def')

    source = get_new_source(target, kind, filepath)
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


def reload_function(target, filepath: str):
    "Get the new function object corresponding to the target function."
    return reload_target(target, 'def', filepath)


class GenericReloadr:

    def _timer_reload(self, interval=1):
        "Reload the target every `interval` seconds."
        while True:
            self._reload()
            sleep(interval)

    def _start_timer_reload(self, interval=1):
        "Start a thread that reloads the target every `interval` seconds."
        thread = threading.Thread(target=self._timer_reload)
        thread.start()

    def _start_watch_reload(self):
        "Reload the target based on file changes in the directory"
        observer = Observer()
        filepath = inspect.getsourcefile(self._target)
        filedir = dirname(filepath)

        this = self

        class EventHandler(FileSystemEventHandler):
            def on_modified(self, event):
                this._reload()

        # Sadly, watchdog only operates on directories and not on a file
        # level, so any change within the directory will trigger a reload.
        observer.schedule(EventHandler(), filedir, recursive=False)
        observer.start()


class ClassReloadr(GenericReloadr):

    def __init__(self, target):
        # target is the decorated class/function
        self._target = target
        self._instances = []  # For classes, keep a reference to all instances

    def __call__(self, *args, **kwargs):
        "Override instantiation in order to register a reference to the instance"
        instance = self._target.__call__(*args, **kwargs)
        # Register a reference to the instance
        self._instances.append(weakref.ref(instance))
        return instance

    def __getattr__(self, name):
        "Proxy inspection to the target"
        return self._target.__getattr__(name)

    def _reload(self):
        "Manually reload the class with its new code."
        try:
            self._target = reload_class(self._target)
            # Replace the class reference of all instances with the new class
            for ref in self._instances:
                instance = ref()  # We keep weak references to objects
                if instance:
                    instance.__class__ = self._target
        except ParsingError as error:
            print('ParsingError', error)


class FuncReloadr(GenericReloadr):

    def __init__(self, target):
        # target is the decorated class/function
        self._target = target
        self._filepath = inspect.getsourcefile(target)

    def __call__(self, *args, **kwargs):
        "Proxy function call to the target"
        return self._target.__call__(*args, **kwargs)

    def __getattr__(self, name):
        "Proxy inspection to the target"
        return self._target.__getattr__(name)

    def _reload(self):
        "Manually reload the function with its new code."
        try:
            self._target = reload_function(self._target, self._filepath)
        except ParsingError as error:
            print('ParsingError', error)


def reloadr(target):
    "Main decorator, forwards the target to the appropriate class."
    if isinstance(target, types.FunctionType):
        return FuncReloadr(target)
    else:
        return ClassReloadr(target)
