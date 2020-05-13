from typing import NamedTuple

from .symbol import Symbol
from .typedefs import StateID

_ArcBase = NamedTuple(
    "_ArcBase",
    [
        ("state", StateID),
        ("upper", Symbol),
        ("lower", Symbol),
        ("destination", StateID),
    ],
)


class Arc(_ArcBase):
    """
    An arc (transition) in the FST.
    """

    def __str__(self) -> str:
        if self.upper == self.lower:
            label = str(self.upper)
        else:
            label = str(self.upper) + ":" + str(self.lower)
        return "{:d} ─{:s}→ {:d}".format(self.state, label, self.destination)
