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
from pathlib import Path
from typing import Union
PathLike = Union[str, Path]


class FST:
    @classmethod
    def from_file(self, path: PathLike) -> 'FST':
        ...


FSMParse = namedtuple('FSMParse', 'sigma multichar_symbols graphemes '
                                  'states arcs')


def parse_text(fst_text: str):
    INITIAL_STATE = 0
    PROPS_STATE = 1
    SIGMA_STATE = 2
    ARC_STATE = 3
    ACCEPT_STATE = 4
    state = INITIAL_STATE

    sigma = {}
    arcs = []
    current_state = None

    for line in fst_text.splitlines():
        # Check header
        if line.startswith('##'):
            header = line[2:-2]
            state = {
                'foma-net 1.0': INITIAL_STATE,
                'props': PROPS_STATE,
                'sigma': SIGMA_STATE,
                'states': ARC_STATE,
                'end': ACCEPT_STATE,
            }[header]
        elif state == SIGMA_STATE:
            # Add line to sigma
            idx_str, symbol = line.split()
            idx = int(idx_str)
            sigma[idx] = symbol
        elif state == ARC_STATE:
            # Add an arc
            arc_def = tuple(int(x) for x in line.split())
            if arc_def == (-1, -1, -1, -1, -1):
                # Sentinel value: there are no more arcs to define.
                continue
            elif len(arc_def) == 2:
                if current_state is None:
                    raise ValueError('No current state')
                label, dest = arc_def
                arcs.append((current_state, dest, label, label))
            elif len(arc_def) == 3:
                if current_state is None:
                    raise ValueError('No current state')
                in_label, out_label, dest = arc_def
                arcs.append((current_state, dest, in_label, out_label))
            elif len(arc_def) == 4:
                src, label, dest, _weight = arc_def
                current_state = src
                arcs.append((src, dest, label, label))
            elif len(arc_def) == 5:
                src, in_label, out_label, dest, _weight = arc_def
                current_state = src
                arcs.append((src, dest, in_label, out_label))

        elif state in (INITIAL_STATE, PROPS_STATE, ACCEPT_STATE):
            pass  # Nothing to do for these states
        else:
            raise ValueError('Invalid state: ' + repr(state))

    # Get rid of epsilon (assumed)
    del sigma[0]

    multichar_symbols = {idx: symbol for idx, symbol in sigma.items()
                         if len(symbol) > 1}
    graphemes = {idx: symbol for idx, symbol in sigma.items()
                 if len(symbol) == 1}

    states = {arc[0] for arc in arcs}

    return FSMParse(sigma=sigma,
                    multichar_symbols=multichar_symbols,
                    graphemes=graphemes,
                    states=states,
                    # exclude arcs out of accepting state
                    arcs={arc for arc in arcs if arc[1] != -1})
