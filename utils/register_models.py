import inspect
from typing import Callable, TypeVar
from django.db.models import Model
from django.contrib.admin.sites import AlreadyRegistered

Module = TypeVar("Module")


def register_models(
    module: Module,
    register_func: Callable[..., None],
    exceptions: list[type[Model]] | None = None,
) -> None:
    exceptions = exceptions or []
    module_name = getattr(module, "__name__", None)

    for _, obj in inspect.getmembers(module, inspect.isclass):
        if not issubclass(obj, Model) or obj is Model:
            continue

        if obj.__module__ != module_name:
            continue

        meta = getattr(obj, "_meta", None)
        if not meta:
            continue

        if meta.abstract or meta.proxy:
            continue

        if obj in exceptions:
            continue

        try:
            register_func(obj)
        except AlreadyRegistered:
            pass
