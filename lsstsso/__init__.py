from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from . import color, filters, get, logging, rsp, scale
from .band import Band
from .color import Color, ColorMatrix

__all__ = [
    "Band",
    "Color",
    "ColorMatrix",
    "color",
    "filters",
    "get",
    "logging",
    "rsp",
    "scale",
]

try:
    __version__ = _version(__name__)
except PackageNotFoundError:  # pragma: no cover
    pass
