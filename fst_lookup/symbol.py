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

from abc import ABC, abstractmethod


class Symbol(ABC):
    """
    A symbol in the FST.
    """
    @abstractmethod
    def accepts(self, other: 'Symbol') -> bool:
        raise NotImplementedError


class Grapheme(Symbol):
    """
    Represents a single graphical character.
    """
    __slots__ = '_char',

    def __init__(self, char: str) -> None:
        assert len(char) == 1
        self._char = char

    def accepts(self, other: Symbol) -> bool:
        if isinstance(other, type(self)):
            return other._char == self._char
        return False

    def __str__(self) -> str:
        return self._char


class MultiCharacterSymbol(Symbol):
    """
    Usually represents a tag or a feature.
    """
    __slots__ = '_tag',

    def __init__(self, tag: str) -> None:
        assert len(tag) > 1
        self._tag = tag

    def accepts(self, other: Symbol) -> bool:
        if isinstance(other, type(self)):
            return other._tag == self._tag
        return False

    def __str__(self) -> str:
        return self._tag
