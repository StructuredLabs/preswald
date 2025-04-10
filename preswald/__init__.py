from importlib.metadata import version


__version__ = version("preswald")

from . import interfaces as _interfaces
from .interfaces import *  # noqa: F403


__all__ = _interfaces.__all__
