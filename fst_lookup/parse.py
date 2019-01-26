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
from typing import List, Dict, Tuple, Set

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


class ParserState(Enum):
    INITIAL = 0
    PROPS = 1
    SIGMA = 2
    ARC = 3
    END = 4



def parse_text(fst_text: str) -> FSTParse:
    # Find all the details here:
    # https://github.com/mhulden/foma/blob/master/foma/io.c#L623-L821

    def parse_arc(arc_def: Tuple[int, ...]) -> None:
        """
        Either:
          - appends an arc to the list;
          - adds an accepting state; or
          - finds the sentinel value
        """
        nonlocal implied_state

        if arc_def == (-1, -1, -1, -1, -1):
            # Sentinel value: there are no more arcs to define.
            return

        if len(arc_def) == 2:
            if implied_state is None:
                raise ValueError('No implied state')
            src = implied_state
            # in/out, target (state num implied)
            in_label, dest = arc_def
            out_label = in_label
        elif len(arc_def) == 3:
            if implied_state is None:
                raise ValueError('No implied state')
            src = implied_state
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
                accepting_states.add(src)
                return
        elif len(arc_def) == 5:
            # FIXME: last is final_state, not weight
            src, in_label, out_label, dest, _weight = arc_def

        implied_state = src
        arcs.append(Arc(state=src, destination=dest, in_label=in_label, out_label=out_label))

    state = ParserState.INITIAL

    # Start with an empty FST
    sigma = {}  # TODO: rename to symbols
    # TODO: keep track of input and output alphabet
    arcs = []  # type: List[Arc]
    accepting_states = set()  # type: Set[StateID]
    implied_state = None

    for line in fst_text.splitlines():
        # Check header
        if line.startswith('##'):
            header = line[2:-2]
            state = {
                'foma-net 1.0': ParserState.INITIAL,
                'props': ParserState.PROPS,
                'sigma': ParserState.SIGMA,
                'states': ParserState.ARC,
                'end': ParserState.END,
            }[header]
        elif state == ParserState.SIGMA:
            # Add an entry to sigma
            idx_str, symbol = line.split()
            idx = int(idx_str)
            sigma[idx] = symbol
        elif state == ParserState.ARC:
            # Add an arc
            arc_def = tuple(int(x) for x in line.split())
            parse_arc(arc_def)
        elif state == ParserState.PROPS:
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
        elif state in (ParserState.INITIAL, ParserState.END):
            pass  # Nothing to do for these states
        else:
            raise ValueError('Invalid state: ' + repr(state))
        # TODO: error when there appears to be more than one model

    # After parsing, we should be in the ##end## state.
    assert state == ParserState.END

    # Get rid of epsilon (it is always assumed!)
    del sigma[0]

    multichar_symbols = {idx: symbol for idx, symbol in sigma.items()
                         if len(symbol) > 1}
    graphemes = {idx: symbol for idx, symbol in sigma.items()
                 if len(symbol) == 1}

    states = {arc.state for arc in arcs}

    return FSTParse(multichar_symbols=multichar_symbols,
                    graphemes=graphemes,
                    arcs=set(arcs),
                    intermediate_states=states,
                    accepting_states=accepting_states)
