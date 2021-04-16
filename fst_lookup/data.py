"""
Classes that define data in the FST.
"""

from .typedefs import StateID


try:
    from ._fst_lookup import Arc
except ImportError:
    from .fallback_data import Arc  # type: ignore
