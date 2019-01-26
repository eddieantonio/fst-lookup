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

from collections import namedtuple
from enum import Enum
from typing import List, Dict, Tuple, Set, Optional, Callable

from .data import Arc, StateID, Symbol


# TODO: add difference between input alphabet and output alphabet
#       the union of the two is the output alphabet

class FSTParse(namedtuple('FSTParse', 'multichar_symbols graphemes '
                                      'arcs '
                                      'intermediate_states accepting_states')):
    """
    The parsed data from an FST, in a nice neat pile.
    """

    @property
    def sigma(self) -> Dict[Symbol, str]:
        return {**self.multichar_symbols, **self.graphemes}

    @property
    def states(self):
        return self.intermediate_states | self.accepting_states


class FomaParser:
    """
    Parses a FOMA AT&T file.
    """

    LineParser = Callable[[str], None]

    def __init__(self) -> None:
        self.symbols = {}  # type: Dict[Symbol, str]
        # TODO: keep track of input and output alphabet
        self.arcs = []  # type: List[Arc]
        self.accepting_states = set()  # type: Set[int]
        self.implied_state = None  # type: Optional[int]
        self.handle_line = self.handle_header

    def handle_header(self, line: str):
        # Nothing to do here... yet.
        ...

    def handle_props(self, line: str):
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
        ...
        # Foma will technically accept anything until it sees '##sigma##'
        # but we won't (how do we handle that?)

    def handle_sigma(self, line: str):
        """
        Adds a new entry to the symbol table.
        """
        idx_str, symbol = line.split()
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

        if arc_def == (-1, -1, -1, -1, -1):
            # Sentinel value: there are no more arcs to define.
            return

        if len(arc_def) == 2:
            if self.implied_state is None:
                raise ValueError('No implied state')
            src = self.implied_state
            # in/out, target (state num implied)
            in_label, dest = arc_def
            out_label = in_label
        elif len(arc_def) == 3:
            if self.implied_state is None:
                raise ValueError('No implied state')
            src = self.implied_state
            # in, out, target  (state num implied)
            in_label, out_label, dest = arc_def
        elif len(arc_def) == 4:
            # FIXME: there's a bug here in my interpretation of the final parameter.
            # state num, in/out, target, final state
            src, in_label, dest, _weight = arc_def
            out_label = in_label
            # FIXME: this is a STATE WITHOUT TRANSITIONS
            if in_label == -1 or dest == -1:
                # This is an accepting state
                self.accepting_states.add(src)
                return
        elif len(arc_def) == 5:
            # FIXME: last is final_state, not weight
            src, in_label, out_label, dest, _weight = arc_def

        self.implied_state = src
        self.arcs.append(Arc(state=src, destination=dest, in_label=in_label, out_label=out_label))

    def handle_end(self, line: str):
        # Nothing to do here. Yet.
        ...

    def parse_text(self, fst_text: str) -> FSTParse:
        # Find all the details here:
        # https://github.com/mhulden/foma/blob/master/foma/io.c#L623-L821
        for line in fst_text.splitlines():
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
                self.handle_line(line.strip())
            # TODO: error when there appears to be more than one model

        # After parsing, we should be in the ##end## state.
        assert self.handle_line == self.handle_end

        # Get rid of epsilon (it is always assumed!)
        del self.symbols[Symbol(0)]

        multichar_symbols = {idx: symbol for idx, symbol in self.symbols.items()
                             if len(symbol) > 1}
        graphemes = {idx: symbol for idx, symbol in self.symbols.items()
                     if len(symbol) == 1}

        states = {arc.state for arc in self.arcs}

        return FSTParse(multichar_symbols=multichar_symbols,
                        graphemes=graphemes,
                        arcs=set(self.arcs),
                        intermediate_states=states,
                        accepting_states=self.accepting_states)


def parse_text(att_text: str) -> FSTParse:
    """
    Parse the text of a FOMA binary FST. The text is retrieved by gunzip'ing
    the file.
    FOMA text is very similar to an AT&T format FST.
    """
    return FomaParser().parse_text(att_text)
