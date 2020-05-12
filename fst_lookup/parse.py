#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright 2019 Eddie Antonio Santos <easantos@ualberta.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
)

from ._parse import parse_arc_definition as parse_arc_definition_line  # type: ignore
from .data import Arc, StateID
from .flags import (
    Clear,
    DisallowFeature,
    DisallowValue,
    FlagDiacritic,
    Positive,
    RequireFeature,
    RequireValue,
    Unify,
)
from .symbol import Epsilon, Grapheme, Identity, MultiCharacterSymbol, Symbol, Unknown

try:
    # There should be a C extension to make parsing slightly faster
    from ._parse import parse_arc_definition as parse_arc_definition_line
except ImportError:

    def parse_arc_definition_line(line: str) -> Tuple[int, ...]:
        return tuple(int(num) for num in line.split())


FLAG_PATTERN = re.compile(
    r"""
    ^@(?:
        [UPNRDE] [.] (?:\w|-)+ [.] (?:\w|-)+ |
        [RDC]    [.] (?:\w|-)+
    )@$
""",
    re.VERBOSE,
)


class FSTParseError(Exception):
    """
    Raise when something goes wrong parsing the FSTs.
    """


class SymbolTable:
    """
    Keeps track of ALL of the symbols in an FST.
    """

    def __init__(self) -> None:
        # TODO: differentiate between input alphabet and output alphabet
        #       the union of input and output is sigma
        self._symbols = {}  # type: Dict[int, Symbol]

    def __getitem__(self, idx: int):
        return self._symbols[idx]

    def add(self, symbol_id: int, symbol: Symbol) -> None:
        """
        Add a symbol to the symbol table.
        """
        if symbol_id in self._symbols:
            raise FSTParseError(
                "Duplicate symbols for index %d: old: %r; new: %r"
                % (symbol_id, self[symbol_id], symbol)
            )
        self._symbols[symbol_id] = symbol

    @property
    def sigma(self) -> Dict[int, Symbol]:
        regular_symbol = (Grapheme, MultiCharacterSymbol, FlagDiacritic)
        return {k: v for k, v in self._symbols.items() if isinstance(v, regular_symbol)}

    @property
    def has_epsilon(self) -> bool:
        return 0 in self._symbols


class FSTParse(
    NamedTuple(
        "FSTParse",
        [
            ("symbols", SymbolTable),
            ("arcs", Set[Arc]),
            ("intermediate_states", Set[StateID]),
            ("accepting_states", Set[StateID]),
        ],
    )
):
    """
    The parsed data from an FST, in a nice neat pile.
    """

    @property
    def multichar_symbols(self) -> Dict[int, MultiCharacterSymbol]:
        return {
            i: sym
            for i, sym in self.symbols.sigma.items()
            if isinstance(sym, MultiCharacterSymbol)
        }

    @property
    def flag_diacritics(self) -> Dict[int, FlagDiacritic]:
        return {
            i: sym
            for i, sym in self.symbols.sigma.items()
            if isinstance(sym, FlagDiacritic)
        }

    @property
    def graphemes(self) -> Dict[int, Grapheme]:
        return {
            i: sym for i, sym in self.symbols.sigma.items() if isinstance(sym, Grapheme)
        }

    @property
    def sigma(self) -> Dict[int, Symbol]:
        return self.symbols.sigma

    @property
    def states(self):
        return self.intermediate_states | self.accepting_states

    @property
    def has_epsilon(self) -> bool:
        return self.symbols.has_epsilon


class StateParser:
    def __init__(self, symbols: SymbolTable, should_invert_labels: bool):
        self.arcs = []  # type: List[Arc]
        self.symbols = symbols
        self.implied_state = None  # type: Optional[int]
        self.accepting_states = set()  # type: Set[StateID]
        self.invert_labels = should_invert_labels

    def parse(self, line: str):
        """
        Either:
          - appends an arc to the list;
          - adds an accepting state; or
          - finds the sentinel value
        """

        arc_def = parse_arc_definition_line(line)
        num_items = len(arc_def)

        if arc_def == (-1, -1, -1, -1, -1):
            # Sentinel value: there are no more arcs to define.
            return

        if num_items == 2:
            if self.implied_state is None:
                raise ValueError("No implied state")
            src = self.implied_state
            # in/out, target (state num implied)
            in_label, dest = arc_def
            out_label = in_label
        elif num_items == 3:
            if self.implied_state is None:
                raise ValueError("No implied state")
            src = self.implied_state
            # in, out, target  (state num implied)
            in_label, out_label, dest = arc_def
        elif num_items == 4:
            # FIXME: there's a bug here in my interpretation of the final parameter.
            # state num, in/out, target, final state
            src, in_label, dest, _weight = arc_def
            out_label = in_label
            # FIXME: this is a STATE WITHOUT TRANSITIONS
            if in_label == -1 or dest == -1:
                # This is an accepting state
                self.accepting_states.add(StateID(src))
                return
        elif num_items == 5:
            # FIXME: last is final_state, not weight
            src, in_label, out_label, dest, _weight = arc_def

        self.implied_state = src
        # Super important! make sure the order of these arguments is
        # consistent with the definition of Arc
        upper_label, lower_label = self.symbols[in_label], self.symbols[out_label]
        if self.invert_labels:
            upper_label, lower_label = lower_label, upper_label
        arc = Arc(StateID(src), upper_label, lower_label, StateID(dest))
        self.arcs.append(arc)


class FomaParser:
    """
    Parses a FOMA file, in plain-text.
    """

    LineParser = Callable[[str], None]

    def __init__(self, invert_labels: bool) -> None:
        self.symbols = SymbolTable()
        self.invert_labels = invert_labels

    def finalize(self) -> FSTParse:
        states = {StateID(arc.state) for arc in self.arcs}
        return FSTParse(
            symbols=self.symbols,
            arcs=set(self.arcs),
            intermediate_states=states,
            accepting_states=self.accepting_states,
        )

    def parse_header(self, lines: Iterator[str]):
        if next(lines) != "##foma-net 1.0##":
            raise FSTParseError("Could not parse header")

    def parse_props(self, lines: Iterator[str]):
        if next(lines) != "##props##":
            raise FSTParseError("Could not parse props")

        _line = next(lines)

        # TODO: parse:
        #  - arity
        #  - arc_count
        #  - state_count
        #  - line_count
        #  - final_count
        #  - path_count
        #  - is_deterministic
        #  - is_pruned
        #  - is_minimized
        #  - is_epsilon_free
        #  - is_loop_free
        #  - is_completed
        #  - name

        # Foma will technically accept anything until it sees '##sigma##'
        # but we won't, as that is gross.

    def parse_body(self, lines: Iterator[str]):
        """
        Handles the following sections:
         - ##sigma##
         - ##states##
         - ##end##
        """

        if next(lines) != "##sigma##":
            raise FSTParseError("Expected sigma")
        leftover = self.parse_sigma(lines)

        if leftover != "##states##":
            raise FSTParseError("Expected states")
        leftover = self.parse_states(lines)

        if leftover != "##end##":
            raise FSTParseError("Expected end")

    def ensure_file_contains_only_one_fst(self, lines: Iterator[str]):
        """
        This should be immediately after seeing the ##end## header.
        """
        try:
            next(lines)
        except StopIteration:
            pass
        else:
            raise FSTParseError("Cannot handle multiple FSTs")

    def parse_states(self, lines: Iterator[str]) -> str:
        line = next(lines)
        state_parse = StateParser(self.symbols, self.invert_labels)
        handle_states = state_parse.parse
        while not line.startswith("##"):
            handle_states(line)
            line = next(lines)

        self.arcs = state_parse.arcs
        self.accepting_states = state_parse.accepting_states

        return line

    def parse_sigma(self, lines: Iterator[str]) -> str:
        """
        Adds a new entry to the symbol table.
        """
        line = next(lines)
        while not line.startswith("##"):
            idx_str, _space, symbol_text = line.partition("\N{SPACE}")
            idx = int(idx_str)
            self.symbols.add(idx, parse_symbol(symbol_text))
            line = next(lines)

        return line

    def parse_text(self, fst_text: str) -> FSTParse:
        lines = iter(fst_text.splitlines())

        # Parse section by section
        self.parse_header(lines)
        self.parse_props(lines)
        self.parse_body(lines)
        self.ensure_file_contains_only_one_fst(lines)

        return self.finalize()


def parse_text(att_text: str, invert_labels: bool = False) -> FSTParse:
    """
    Parse the text of a FOMA binary FST. The text is retrieved by gunzip'ing
    the file.

    FOMA text is very similar to an AT&T format FST.
    """
    return FomaParser(invert_labels).parse_text(att_text)


def parse_symbol(symbol: str) -> Symbol:
    if FLAG_PATTERN.match(symbol):
        return parse_flag(symbol)
    elif symbol == "@_EPSILON_SYMBOL_@":
        return Epsilon
    elif symbol == "@_UNKNOWN_SYMBOL_@":
        return Unknown
    elif symbol == "@_IDENTITY_SYMBOL_@":
        return Identity
    elif symbol.startswith("@") and symbol.endswith("@"):
        raise NotImplementedError
    elif len(symbol) > 1:
        return MultiCharacterSymbol(symbol)
    elif len(symbol) == 1:
        return Grapheme(symbol)
    raise NotImplementedError


def parse_flag(flag_diacritic: str) -> FlagDiacritic:
    assert FLAG_PATTERN.match(flag_diacritic)
    opcode, *arguments = flag_diacritic.strip("@").split(".")
    if opcode == "U" and len(arguments) == 2:
        return Unify(*arguments)
    elif opcode == "P" and len(arguments) == 2:
        return Positive(*arguments)
    elif opcode == "R" and len(arguments) == 2:
        return RequireValue(*arguments)
    elif opcode == "R" and len(arguments) == 1:
        return RequireFeature(*arguments)
    elif opcode == "D" and len(arguments) == 1:
        return DisallowFeature(*arguments)
    elif opcode == "D" and len(arguments) == 2:
        return DisallowValue(*arguments)
    elif opcode == "C" and len(arguments) == 1:
        return Clear(arguments[0])
    raise ValueError("Cannot parse " + flag_diacritic)
