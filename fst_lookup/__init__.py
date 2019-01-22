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
import gzip
from collections import namedtuple, defaultdict
from enum import Enum
from pathlib import Path
from typing import (
        Union, Tuple, List, Set, Iterable, Dict, NewType, Sequence, Callable
)


PathLike = Union[str, Path]
StateID = NewType('StateID', int)
Symbol = int  # TODO: fancy union of int

INVALID = -1
EPSILON = 0


class FST:
    def __init__(self, parse: 'FSTParse') -> None:
        self.initial_state = min(parse.states)
        self.accepting_states = frozenset(parse.accepting_states)
        self.sigma = dict(parse.sigma)  # Type: Dict[int, str]
        self.inverse_sigma = {text: idx for idx, text in self.sigma.items()}
        self.multichar_symbols = parse.multichar_symbols
        self.graphemes = parse.graphemes

        self.arcs_from = defaultdict(set)  # type: Dict[StateID, Set[Arc]]
        for arc in parse.arcs:
            self.arcs_from[arc.state].add(arc)

    def lookup(self, surface_form: str) -> Iterable[Tuple[str, ...]]:
        state = self.initial_state
        symbols = []

        # tokenize the surface form to symbols
        text = surface_form
        pattern = re.compile('|'.join(re.escape(entry) for entry in self.sigma.values()))
        while text:
            match = pattern.match(text)
            if not match:
                raise ValueError("Cannot symbolify form: " + repr(surface_form))
            # Convert to a symbol
            symbols.append(self.inverse_sigma[match.group(0)])
            text = text[match.end():]

        for transduction in self._lookup_state(self.initial_state, symbols, []):
            yield self.format_transduction(transduction)

    def format_transduction(self, transduction: Iterable[Symbol]) -> Tuple[str, ...]:
        # TODO: REFACTOR THIS GROSS FUNCTION
        def generate():
            current_lemma = ''
            for symbol in transduction:
                if symbol == EPSILON:
                    if current_lemma:
                        yield current_lemma
                        current_lemma = ''
                    # ignore epsilons
                    continue
                elif symbol in self.multichar_symbols:
                    if current_lemma:
                        yield current_lemma
                        current_lemma = ''
                    yield self.sigma[symbol]
                else:
                    assert symbol in self.graphemes
                    current_lemma += self.sigma[symbol]

            if current_lemma:
                yield current_lemma
                current_lemma = ''

        return tuple(generate())

    # TODO: Sequence[Symbol], List[Symbol]
    def _lookup_state(self,
                      state: StateID,
                      symbols: Sequence[int],
                      transduction: List[int]) -> Iterable[Tuple[int, ...]]:

        if state in self.accepting_states:
            # TODO: Handle cyclic accepting state.
            if len(symbols) > 0:
                return
            yield tuple(transduction)
            return

        for arc in self.arcs_from[state]:
            next_symbol = symbols[0] if len(symbols) else INVALID
            if arc.lower == EPSILON:
                # Transduce WITHOUT consuming input
                transduction.append(arc.upper)
                yield from self._lookup_state(arc.destination, symbols, transduction)
                transduction.pop()
            elif arc.lower == next_symbol:
                # Transduce, consuming the symbol as a label
                transduction.append(arc.upper)
                yield from self._lookup_state(arc.destination, symbols[1:], transduction)
                transduction.pop()

    @classmethod
    def from_file(cls, path: PathLike) -> 'FST':
        """
        Read the FST as output by FOMA (gzip'd AT&T format).
        """
        with gzip.open(str(path), 'rt', encoding='UTF-8') as text_file:
            return cls.from_text(text_file.read())

    @classmethod
    def from_text(self, att_text: str) -> 'FST':
        """
        Parse the FST in AT&T's transducer text format.
        """
        parse = parse_text(att_text)
        return FST(parse)


class FSTParse(namedtuple('FSTParse', 'multichar_symbols graphemes '
                                      'arcs '
                                      'intermediate_states accepting_states')):
    """
    The parsed data from an FST, in a nice neat pile.
    """

    @property
    def sigma(self) -> Dict[int, str]:
        return {**self.multichar_symbols, **self.graphemes}

    @property
    def states(self):
        return self.intermediate_states | self.accepting_states


class Arc(namedtuple('ArcBase', 'state in_label out_label destination')):
    """
    An arc (transition) in the FST.
    """
    def __str__(self) -> str:
        return self.debug_string(labels=str)

    def debug_string(self, labels: Callable[[int], str]) -> str:
        return '{:d} – {:s}:{:s} → {:d}'.format(
                self.state,
                labels(self.in_label),
                labels(self.out_label),
                self.destination
        )

    @property
    def lower(self) -> Symbol:
        return self.out_label  # type: ignore

    @property
    def upper(self) -> Symbol:
        return self.in_label  # type: ignore


def parse_text(fst_text: str) -> FSTParse:
    class ParserState:
        INITIAL = 0
        PROPS = 1
        SIGMA = 2
        ARC = 3
        END = 4

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
            in_label, dest = arc_def
            out_label = in_label
        elif len(arc_def) == 3:
            if implied_state is None:
                raise ValueError('No implied state')
            src = implied_state
            in_label, out_label, dest = arc_def
        elif len(arc_def) == 4:
            src, in_label, dest, _weight = arc_def
            out_label = in_label
            if in_label == -1 or dest == -1:
                # This is an accepting state
                accepting_states.add(src)
                return
        elif len(arc_def) == 5:
            src, in_label, out_label, dest, _weight = arc_def

        implied_state = src
        arcs.append(Arc(state=src, destination=dest, in_label=in_label, out_label=out_label))

    state = ParserState.INITIAL

    # Start with an empty FST
    sigma = {}
    arcs = []  # type: List[Arc]
    accepting_states = set()  # type: Set[int]
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
        elif state in (ParserState.INITIAL, ParserState.PROPS, ParserState.END):
            pass  # Nothing to do for these states
        else:
            raise ValueError('Invalid state: ' + repr(state))

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
