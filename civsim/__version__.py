"""Set __version__ given .scmversion."""

try:
    from .scmversion import __version__
except ImportError:
    __version__ = 'unknown'
