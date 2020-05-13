from typing import Tuple
from .typedefs import StateID
from .symbol import Symbol

def parse_arc_definition(line: str) -> Tuple[int, ...]: ...

class Arc:
    def __init__(self, state: int, upper: Symbol, lower: Symbol, destination: int) -> None: ...
    @property
    def state(self) -> int: ...
    @property
    def upper(self) -> Symbol: ...
    @property
    def lower(self) -> Symbol: ...
    @property
    def destination(self) -> int: ...
