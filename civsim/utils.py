"""Miscellaneous civsim methods."""

from civsim.config import LOGFILE_SAVE_LOCATION


def log(*args, end='\n'):
    """Append output stream to a file."""
    with open(LOGFILE_SAVE_LOCATION, 'a') as w:
        w.write(' '.join([str(arg) for arg in args]) + end)


def clamp(val, nmin=0, nmax=1):
    """Restrict value between nmin and nmax."""
    return max(nmin, min(val, nmax))
