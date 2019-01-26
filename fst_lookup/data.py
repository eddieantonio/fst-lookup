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
from typing import Callable, NewType

Symbol = NewType('Symbol', int)
StateID = NewType('StateID', int)


class Arc(namedtuple('ArcBase', 'state in_label out_label destination')):
    """
    An arc (transition) in the FST.
    """
    def __str__(self) -> str:
        return self.debug_string(labels=str)

    def debug_string(self, labels: Callable[[Symbol], str]) -> str:
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