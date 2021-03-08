"""
Makes sure that the '@' is a valid symbol in an FST.
"""

from fst_lookup.parse import parse_text

FST_WITH_AT_TEXT = """##foma-net 1.0##
##props##
2 390211 90019 390213 5 -1 1 2 2 1 0 2
##sigma##
0 @_EPSILON_SYMBOL_@
1 @_UNKNOWN_SYMBOL_@
2 @_IDENTITY_SYMBOL_@
3 @
##states##
-1 -1 -1 -1 -1
##end##
"""


def test_parse_at_symbol():
    # It used to throw "NotImplementedError"
    parse_text(FST_WITH_AT_TEXT)
