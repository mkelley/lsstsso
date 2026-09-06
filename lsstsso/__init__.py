from importlib.metadata import version as _version, PackageNotFoundError

from . import filters  # noqa: F401
from . import get  # noqa: F401
from . import logging  # noqa: F401
from . import scale  # noqa: F401
from .band import Band  # noqa: F401
from .rsp import RSP  # noqa: F401

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    pass
