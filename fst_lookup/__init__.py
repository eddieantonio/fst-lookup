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
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple, Union

from .data import Arc, StateID, Symbol
from .parse import FSTParse, parse_text

PathLike = Union[str, Path]

INVALID = Symbol(-1)
EPSILON = Symbol(0)


class FST:
    """
    A finite-state transducer that can convert between one string and a set of
    output strings.
    """

    def __init__(self, parse: FSTParse) -> None:
        self.initial_state = min(parse.states)
        self.accepting_states = frozenset(parse.accepting_states)
        self.sigma = dict(parse.sigma)
        self.inverse_sigma = {text: idx for idx, text in self.sigma.items()}
        self.multichar_symbols = parse.multichar_symbols
        self.graphemes = parse.graphemes

        self.arcs_from = defaultdict(set)  # type: Dict[StateID, Set[Arc]]
        for arc in parse.arcs:
            self.arcs_from[arc.state].add(arc)

    def lookup(self, surface_form: str) -> Iterable[Tuple[str, ...]]:
        """
        Given a surface form, this yields all possible analyses in the FST.
        """
        state = self.initial_state
        symbols = list(self.to_symbols(surface_form))

        for transduction in self._lookup_state(self.initial_state, symbols, []):
            yield tuple(self._format_transduction(transduction))

    def _format_transduction(self, transduction: Iterable[Symbol]) -> Iterable[str]:
        """
        """
        # TODO: REFACTOR THIS GROSS FUNCTION
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

    def to_symbols(self, surface_form: str) -> Iterable[Symbol]:
        """
        Tokenizes a form into symbols.
        """
        text = surface_form
        pattern = re.compile('|'.join(re.escape(entry) for entry in self.sigma.values()))
        while text:
            match = pattern.match(text)
            if not match:
                raise ValueError("Cannot symbolify form: " + repr(surface_form))
            # Convert to a symbol
            yield self.inverse_sigma[match.group(0)]
            text = text[match.end():]

    def _lookup_state(
            self, state: StateID,
            symbols: List[Symbol],
            transduction: List[Symbol]
            ) -> Iterable[Tuple[Symbol, ...]]:

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
