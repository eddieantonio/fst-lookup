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

from typing import Callable, NamedTuple, NewType

from .symbol import Symbol

StateID = NewType('StateID', int)


class Arc(NamedTuple('ArcBase', [('state', StateID),
                                 ('upper', Symbol),
                                 ('lower', Symbol),
                                 ('destination', StateID)])):
    """
    An arc (transition) in the FST.
    """
    def __str__(self) -> str:
        return self.debug_string(labels=str)

    def debug_string(self, labels: Callable[[Symbol], str]) -> str:
        # TODO: compact notation when upper == lower
        return '{:d} – {:s}:{:s} → {:d}'.format(
                self.state,
                labels(self.in_label),
                labels(self.out_label),
                self.destination
        )

    @property
    def out_label(self) -> Symbol:
        return self.lower

    @property
    def in_label(self) -> Symbol:
        return self.upper
