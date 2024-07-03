"""
Fallback data types, implemented in Python, for platforms that cannot build
the C extension.
"""

from .symbol import Symbol
from .typedefs import StateID


class Arc:
    """
    An arc (transition) in the FST.
    """

    __slots__ = ("_state", "_upper", "_lower", "_destination")

    def __init__(
        self, state: StateID, upper: Symbol, lower: Symbol, destination: StateID
    ) -> None:
        self._state = state
        self._upper = upper
        self._lower = lower
        self._destination = destination

    @property
    def state(self) -> StateID:
        return self._state

    @property
    def upper(self) -> Symbol:
        return self._upper

    @property
    def lower(self) -> Symbol:
        return self._lower

    @property
    def destination(self) -> StateID:
        return self._destination

    def __eq__(self, other) -> bool:
        if not isinstance(other, Arc):
            return False
        return (
            self._state == other._state
            and self._upper == other._upper
            and self._lower == other._lower
            and self._destination == other._destination
        )

    def __hash__(self) -> int:
        return self._state + (hash(self._upper) ^ hash(self._lower))

    def __str__(self) -> str:
        if self._upper == self._lower:
            label = str(self._upper)
        else:
            label = str(self._upper) + ":" + str(self._lower)

        return "{:d} -{:s}-> {:d}".format(self._state, label, self._destination)
