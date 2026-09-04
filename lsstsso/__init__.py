from importlib.metadata import version as _version, PackageNotFoundError
from logging import basicConfig

from . import get  # noqa: F401
from .band import Band  # noqa: F401
from .plot import markers  # noqa: F401
from .rsp import RSP  # noqa: F401
from .scale import color_scales, scale_by_geometry  # noqa: F401

basicConfig()

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    pass
