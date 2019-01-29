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
from collections import namedtuple
from enum import Enum
from typing import List, Dict, Tuple, Set, Optional, Callable

from .data import Arc, StateID, Symbol


FLAG_PATTERN = re.compile(r'''
    ^@(?:
        [UPNRDE][.]\w+[.]\w+ |
        [RDC][.]\w+
    )@$
''', re.VERBOSE)


class FSTParseError(Exception):
    """
    Raise when something goes wrong parsing the FSTs.
    """


class FlagDiacritic:
    """
    Base class for all flag diacritics
    """

    opcode = '!!INVALID!!'

    def __init__(self, feature: str, value: str = None) -> None:
        self.feature = feature
        if value is not None:
            self.value = value

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        if hasattr(self, 'value'):
            return self.feature == other.feature and self.value == other.value
        else:
            return self.feature == other.feature

    def __str__(self) -> str:
        if hasattr(self, 'value'):
            return '@{}.{}.{}@'.format(self.opcode, self.feature, self.value)
        else:
            return '@{}.{}@'.format(self.opcode, self.feature)


class Clear(FlagDiacritic):
    opcode = 'C'


class Disallow(FlagDiacritic):
    opcode = 'D'


class Positive(FlagDiacritic):
    opcode = 'P'


# TODO: add difference between input alphabet and output alphabet
#       the union of the two is the output alphabet

class FSTParse(namedtuple('FSTParse', 'multichar_symbols graphemes flag_diacritics '
                                      'arcs '
                                      'intermediate_states accepting_states')):
    """
    The parsed data from an FST, in a nice neat pile.
    """

    @property
    def sigma(self) -> Dict[Symbol, str]:
        return {**self.multichar_symbols,
                **self.flag_diacritics,
                **self.graphemes}

    @property
    def states(self):
        return self.intermediate_states | self.accepting_states


class FomaParser:
    """
    Parses a FOMA file, in plain-text.
    """

    LineParser = Callable[[str], None]

    def __init__(self) -> None:
        self.symbols = {}  # type: Dict[Symbol, str]
        # TODO: keep track of input and output alphabet
        self.arcs = []  # type: List[Arc]
        self.accepting_states = set()  # type: Set[int]
        self.implied_state = None  # type: Optional[int]
        self.handle_line = self.handle_header
        self.has_seen_header = False

    def handle_header(self, line: str):
        # Nothing to do here... yet.
        ...

    def handle_props(self, line: str):
        """
        """
        if self.has_seen_header:
            raise FSTParseError('Cannot handle multiple FSTs')
        self.has_seen_header = True

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

    def handle_sigma(self, line: str):
        """
        Adds a new entry to the symbol table.
        """
        idx_str, _space, symbol = line.partition('\N{SPACE}')
        idx = int(idx_str)
        self.symbols[Symbol(idx)] = symbol

    def handle_states(self, line: str):
        """
        Either:
          - appends an arc to the list;
          - adds an accepting state; or
          - finds the sentinel value
        """

        arc_def = tuple(int(num) for num in line.split())
        num_items = len(arc_def)

        if arc_def == (-1, -1, -1, -1, -1):
            # Sentinel value: there are no more arcs to define.
            return

        if num_items == 2:
            if self.implied_state is None:
                raise ValueError('No implied state')
            src = self.implied_state
            # in/out, target (state num implied)
            in_label, dest = arc_def
            out_label = in_label
        elif num_items == 3:
            if self.implied_state is None:
                raise ValueError('No implied state')
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
                self.accepting_states.add(src)
                return
        elif num_items == 5:
            # FIXME: last is final_state, not weight
            src, in_label, out_label, dest, _weight = arc_def

        self.implied_state = src
        # Super important! make sure the order of these arguments is
        # consistent with the definition of Arc
        self.arcs.append(Arc(src, in_label, out_label, dest))

    def handle_end(self, line: str):
        # Nothing to do here. Yet.
        ...

    def parse_line(self, line: str):
        # Find all the details here:
        # https://github.com/mhulden/foma/blob/master/foma/io.c#L623-L821
        # Check header
        if line.startswith('##'):
            header = line[2:-2]
            self.handle_line = {
                'foma-net 1.0': self.handle_header,
                'props': self.handle_props,
                'sigma': self.handle_sigma,
                'states': self.handle_states,
                'end': self.handle_end,
            }[header]
        else:
            self.handle_line(line.rstrip('\n'))

    def finalize(self) -> FSTParse:
        # After parsing, we should be in the ##end## state.
        assert self.handle_line == self.handle_end

        # Get rid of special symbols:
        # 0 @_EPSILON_SYMBOL_@
        # 1 @_UNKNOWN_SYMBOL_@
        # 2 @_IDENTITY_SYMBOL_@
        for idx in Symbol(0), Symbol(1), Symbol(2):
            if idx in self.symbols:
                del self.symbols[idx]

        flag_diacritics = {idx: symbol for idx, symbol in self.symbols.items()
                           if FLAG_PATTERN.match(symbol)}
        multichar_symbols = {idx: symbol for idx, symbol in self.symbols.items()
                             if len(symbol) > 1 and idx not in flag_diacritics}
        graphemes = {idx: symbol for idx, symbol in self.symbols.items()
                     if len(symbol) == 1}

        states = {arc.state for arc in self.arcs}

        return FSTParse(multichar_symbols=multichar_symbols,
                        flag_diacritics=flag_diacritics,
                        graphemes=graphemes,
                        arcs=set(self.arcs),
                        intermediate_states=states,
                        accepting_states=self.accepting_states)

    def parse_text(self, fst_text: str) -> FSTParse:
        for line in fst_text.splitlines():
            self.parse_line(line)

        return self.finalize()


def parse_text(att_text: str) -> FSTParse:
    """
    Parse the text of a FOMA binary FST. The text is retrieved by gunzip'ing
    the file.

    FOMA text is very similar to an AT&T format FST.
    """
    return FomaParser().parse_text(att_text)


def parse_flag(flag_diacritic: str) -> FlagDiacritic:
    assert FLAG_PATTERN.match(flag_diacritic)
    opcode, *arguments = flag_diacritic.strip('@').split('.')
    if opcode == 'C':
        return Clear(arguments[0])
    elif opcode == 'D':
        return Disallow(*arguments)
    elif opcode == 'P':
        return Positive(*arguments)
    raise ValueError('Cannot parse ' + flag_diacritic)
