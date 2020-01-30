"""Reloadr - Python library for hot code reloading
(c) 2015-2020 Hugo Herter
"""

from __future__ import annotations

from typing import Any
from time import sleep

import inspect
import threading
import types
import weakref
from abc import abstractmethod
from os.path import dirname, abspath
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer

__author__ = "Hugo Herter"
__version__ = '0.4.0'


def get_new_source(target, kind: str) -> str:
    """Get the new source code of the target if given kind ('class' or 'def').

    This works by using RedBaron to fetch the source code of the first object
    that shares its name and kind with the target, inside the Python file from
    which the target has been loaded.
    """
    assert kind in ('class', 'def')
    source = inspect.getsource(target)

    if kind == 'def':
        # `inspect.getsource` will not return the decorators in the source of classes,
        # but will return them in the source of functions.
        source = source.replace("@autoreload\n", "")
    return source


def reload_target(target, kind: str):
    """Get the new target class/function corresponding to the given target.

    This works by executing the new source code of the target inside the
    namespace of its module (for imports, ...), and then returning the variable
    sharing its name with the target from the new local namespace.
    """
    assert kind in ('class', 'def')

    source = get_new_source(target, kind)
    module = inspect.getmodule(target)
    # We will populate these locals using exec()
    locals_: dict = {}
    # module.__dict__ is the namespace of the module
    exec(source, module.__dict__, locals_)
    return locals_[target.__name__]


def reload_class(target):
    """Get the new class object corresponding to the target class."""
    return reload_target(target, 'class')


def reload_function(target):
    """Get the new function object corresponding to the target function."""
    return reload_target(target, 'def')


class GenericReloadr:
    _target: Any

    @abstractmethod
    def _reload(self) -> None:
        raise NotImplementedError()

    def _timer_reload(self, interval: float = 1.0) -> None:
        """Reload the target every `interval` seconds."""
        while True:
            self._reload()
            sleep(interval)

    def _start_timer_reload(self, interval=1) -> None:
        """Start a thread that reloads the target every `interval` seconds."""
        thread = threading.Thread(target=self._timer_reload)
        thread.start()

    def _start_watch_reload(self) -> None:
        """Reload the target based on file changes in the directory"""
        observer = Observer()
        filepath = inspect.getsourcefile(self._target)
        assert filepath, f"No file path found for {self._target}"
        fileabspath = abspath(filepath)
        filedir = dirname(fileabspath)

        this = self

        class EventHandler(FileSystemEventHandler):
            def on_modified(self, event: FileModifiedEvent):
                # All files within the watched directory will trigger
                # an event, so we filter to only reload when the target
                # file is changed.
                if event.is_directory:
                    return
                if event.src_path == fileabspath:
                    this._reload()

        # Sadly, watchdog only operates on directories and not on a file
        # level, so any change within the directory will trigger a reload.
        observer.schedule(EventHandler(), filedir, recursive=False)
        observer.start()


class ClassReloadr(GenericReloadr):

    def __init__(self, target):
        # target is the decorated class/function
        self._target = target
        self._original_target = target
        self._instances = []  # For classes, keep a reference to all instances

    def __call__(self, *args, **kwargs):
        """Override instantiation in order to register a reference to the instance"""
        instance = self._target.__call__(*args, **kwargs)
        # Register a reference to the instance
        self._instances.append(weakref.ref(instance))
        return instance

    def __getattr__(self, name):
        """Proxy inspection to the target"""
        return self._target.__getattr__(name)

    def _reload(self) -> None:
        """Manually reload the class with its new code."""
        try:
            self._target = reload_class(self._target)
            # Replace the class reference of all instances with the new class
            for ref in self._instances:
                instance = ref()  # We keep weak references to objects
                if instance:
                    instance.__class__ = self._target
        except SyntaxError as error:
            print('SyntaxError', error)


class FuncReloadr(GenericReloadr):

    def __init__(self, target):
        # target is the decorated class/function
        self._target = target
        self._original_target = target

    def __call__(self, *args, **kwargs):
        """Proxy function call to the target"""
        return self._target.__call__(*args, **kwargs)

    def __getattr__(self, name):
        """Proxy inspection to the target"""
        return self._target.__getattr__(name)

    def _reload(self) -> None:
        """Manually reload the function with its new code."""
        try:
            self._target = reload_function(self._original_target)
        except SyntaxError as error:
            print('SyntaxError', error)


def reloadr(target):
    """Main decorator, forwards the target to the appropriate class."""
    if isinstance(target, types.FunctionType):
        return FuncReloadr(target)
    else:
        return ClassReloadr(target)


def autoreload(target):
    """Decorator that immediately starts watching the source file in a thread."""
    result = reloadr(target)
    result._start_watch_reload()
    return result
