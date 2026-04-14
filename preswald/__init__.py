from importlib.metadata import version, PackageNotFoundError


try:
    __version__ = version("preswald")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

from . import interfaces as _interfaces
from .interfaces import *  # noqa: F403


__all__ = _interfaces.__all__


# Lazy getter to avoid circular import at startup
def get_workflow():
    from preswald.engine.service import PreswaldService
    return PreswaldService.get_instance()._workflow
