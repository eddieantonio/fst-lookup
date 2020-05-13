from .symbol import Symbol
from .typedefs import StateID


class Arc:
    """
    An arc (transition) in the FST.
    """

    def __init__(
        self, state: StateID, upper: Symbol, lower: Symbol, destination:
        StateID
    ) -> None:
        self._state = state
        self._upper = upper
        self._lower = lower
        self._destination = destination

    @property
    def state(self) -> int:
        return self._state

    @property
    def upper(self) -> Symbol:
        return self._upper

    @property
    def lower(self) -> Symbol:
        return self._lower

    @property
    def destination(self) -> int:
        return self._destination

    def __str__(self) -> str:
        if self.upper == self.lower:
            label = str(self.upper)
        else:
            label = str(self.upper) + ":" + str(self.lower)
        return "{:d} -{:s}-> {:d}".format(self.state, label, self.destination)
