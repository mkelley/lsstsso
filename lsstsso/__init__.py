from importlib.metadata import version as _version, PackageNotFoundError

from . import filters
from . import get
from . import logging
from . import rsp
from . import scale
from .band import Band
from .color import Color, ColorMatrix

__all__ = [
    "filters",
    "get",
    "logging",
    "rsp",
    "scale",
    "Band",
    "Color",
    "ColorMatrix",
]

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    pass
