from importlib.metadata import version as _version, PackageNotFoundError

from .rsp import RSP  # noqa: F401
from . import get  # noqa: F401

try:
    __version__ = _version(__name__)
except PackageNotFoundError:
    pass
