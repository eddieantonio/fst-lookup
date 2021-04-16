import gzip
import re
from collections import defaultdict
from os import PathLike
from pathlib import Path
from typing import (
    Callable,
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Set,
    Tuple,
    Union,
)

from .data import Arc, StateID
from .flags import FlagDiacritic
from .parse import FSTParse, parse_text
from .symbol import Epsilon, Grapheme, MultiCharacterSymbol, Symbol

# Type aliases
RawTransduction = Tuple[Symbol, ...]
# Gets a Symbol from an arc. func(arc: Arc) -> Symbol
SymbolFromArc = Callable[[Arc], Symbol]
# An analysis is a tuple of strings.
Analyses = Iterable[Tuple[str, ...]]

VALID_LABEL_SETTINGS = ["normal", "invert"]


class OutOfAlphabetError(Exception):
    """
    Raised when an input string contains a character outside of the input
    alphabet.
    """


class FST:
    """
    A finite-state transducer that can convert between one string and a set of
    output strings.
    """

    def __init__(self, parse: FSTParse) -> None:
        self.initial_state = min(parse.states)
        self.accepting_states = frozenset(parse.accepting_states)

        self.str2symbol = {
            str(sym): sym for sym in parse.sigma.values() if sym.is_graphical_symbol
        }

        # Prepare a regular expression to symbolify all input.
        # Ensure the longest symbols are first, so that they are match first
        # by the regular expresion.
        symbols = sorted(self.str2symbol.keys(), key=len, reverse=True)
        self.symbol_pattern = re.compile(
            "|".join(re.escape(entry) for entry in symbols)
        )

        self.arcs_from = defaultdict(set)  # type: Dict[StateID, Set[Arc]]
        for arc in parse.arcs:
            self.arcs_from[arc.state].add(arc)

    def analyze(self, surface_form: str) -> Analyses:
        """
        Given a surface form, this yields all possible analyses in the FST.
        """
        try:
            symbols = list(self.to_symbols(surface_form))
        except OutOfAlphabetError:
            return
        analyses = self._transduce(
            symbols,
            get_input_label=lambda arc: arc.lower,
            get_output_label=lambda arc: arc.upper,
        )
        for analysis in analyses:
            yield tuple(self._format_transduction(analysis))

    def generate(self, analysis: str) -> Iterable[str]:
        """
        Given an analysis, this yields all possible surface forms in the FST.
        """
        try:
            symbols = list(self.to_symbols(analysis))
        except OutOfAlphabetError:
            return
        forms = self._transduce(
            symbols,
            get_input_label=lambda arc: arc.upper,
            get_output_label=lambda arc: arc.lower,
        )
        for transduction in forms:
            yield "".join(
                str(symbol) for symbol in transduction if symbol is not Epsilon
            )

    def to_symbols(self, surface_form: str) -> Iterable[Symbol]:
        """
        Tokenizes a form into symbols.
        """
        text = surface_form
        while text:
            match = self.symbol_pattern.match(text)
            if not match:
                raise OutOfAlphabetError("Cannot symbolify form: " + repr(surface_form))
            # Convert to a symbol
            yield self.str2symbol[match.group(0)]
            text = text[match.end() :]

    @classmethod
    def from_file(cls, path: PathLike, labels: str = "normal") -> "FST":
        """
        Read the FST as output by FOMA.

        `labels` can be one of:
          - "normal" (default): surface form is LOWER label: apply up to
            analyze, apply down to generate; use this if you are following the
            conventions of "Finite State Morphology" by Beesley & Karttunen.
          - "invert": surface form is UPPER label: apply down to analyze, and
            apply up to generate; HFST usually produces FSTs in this style, so
            try to invert FSTs that aren't working using labels="normal".
        """
        with gzip.open(str(path), "rt", encoding="UTF-8") as text_file:
            return cls.from_text(text_file.read(), labels=labels)

    @classmethod
    def from_text(self, att_text: str, labels="normal") -> "FST":
        """
        Parse the FST in the text format (un-gzip'd).
        """
        if labels not in VALID_LABEL_SETTINGS:
            raise ValueError(
                "expected labels to be one of of "
                f"{VALID_LABEL_SETTINGS!r} but instead got {labels!r}"
            )
        parse = parse_text(
            att_text, invert_labels=True if labels == "invert" else False
        )
        return FST(parse)

    def _transduce(
        self,
        symbols: List[Symbol],
        get_input_label: SymbolFromArc,
        get_output_label: SymbolFromArc,
    ):
        yield from Transducer(
            initial_state=self.initial_state,
            symbols=symbols,
            arcs_from=self.arcs_from,
            accepting_states=self.accepting_states,
            get_input_label=get_input_label,
            get_output_label=get_output_label,
        )

    def _format_transduction(self, transduction: Iterable[Symbol]) -> Iterable[str]:
        """
        Formats the transduction by making a few assumptions:

         - Adjacent graphemes should be concatenated
         - Multi-character symbols should stand alone (e.g., +Pl)
         - Epsilons are never emitted in the output
        """

        current_lemma = ""
        for symbol in transduction:
            if symbol is Epsilon:
                # Skip epsilons
                continue
            elif isinstance(symbol, MultiCharacterSymbol):
                # We've seen a previous sequence of graphemes.
                # Output it and reset!
                if current_lemma:
                    yield current_lemma
                    current_lemma = ""
                yield str(symbol)
            else:
                # This MUST be a grapheme. Concatenated it to the output.
                assert isinstance(symbol, Grapheme)
                current_lemma += str(symbol)

        # We may some graphemes remaining. Output them!
        if current_lemma:
            yield current_lemma


class Transducer(Iterable[RawTransduction]):
    """
    Does a single transduction
    """

    def __init__(
        self,
        initial_state: StateID,
        symbols: Iterable[Symbol],
        get_input_label: SymbolFromArc,
        get_output_label: SymbolFromArc,
        accepting_states: FrozenSet[StateID],
        arcs_from: Dict[StateID, Set[Arc]],
    ) -> None:
        self.initial_state = initial_state
        self.symbols = list(symbols)
        self.get_input_label = get_input_label
        self.get_output_label = get_output_label
        self.accepting_states = accepting_states
        self.arcs_from = arcs_from

    def __iter__(self) -> Iterator[RawTransduction]:
        yield from self._accept(self.initial_state, [], [{}])

    def _accept(
        self,
        state: StateID,
        transduction: List[Symbol],
        flag_stack: List[Dict[str, str]],
    ) -> Iterable[RawTransduction]:
        # TODO: Handle a maximum transduction depth, for cyclic FSTs.
        if state in self.accepting_states:
            if len(self.symbols) > 0:
                return
            yield tuple(transduction)

        for arc in self.arcs_from[state]:
            input_label = self.get_input_label(arc)

            if input_label is Epsilon:
                # Transduce WITHOUT consuming input
                transduction.append(self.get_output_label(arc))
                yield from self._accept(arc.destination, transduction, flag_stack)
                transduction.pop()
            elif len(self.symbols) > 0 and input_label == self.symbols[0]:
                # Transduce, consuming the symbol as a label
                transduction.append(self.get_output_label(arc))
                consumed = self.symbols.pop(0)
                yield from self._accept(arc.destination, transduction, flag_stack)
                self.symbols.insert(0, consumed)
                transduction.pop()
            elif input_label.is_flag_diacritic:
                # Evaluate flag diacritic
                flag = input_label
                flags = flag_stack[-1]
                if flag.test(flags):  # type: ignore
                    next_flags = flags.copy()
                    flag.apply(next_flags)  # type: ignore
                    # Transduce WITHOUT consuming input OR emitting output
                    # label (output should be the flag again).
                    assert input_label == self.get_output_label(
                        arc
                    ), "Arc does not have flags on both labels " + repr(arc)
                    yield from self._accept(
                        arc.destination, transduction, flag_stack + [next_flags]
                    )
