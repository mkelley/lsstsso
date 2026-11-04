from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from . import filters, get, logging, rsp, scale
from .band import Band
from .color import Color, ColorMatrix, transform

__all__ = [
    "Band",
    "Color",
    "ColorMatrix",
    "filters",
    "get",
    "logging",
    "rsp",
    "scale",
    "transform",
]

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    pass
