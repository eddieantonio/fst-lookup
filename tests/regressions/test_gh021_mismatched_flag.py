"""
The library should no longer crash when a flag diacrtic on one side of the label is mismatched with
the other side of the label.

See: https://github.com/eddieantonio/fst-lookup/issues/21
"""
from fst_lookup import FST

# A transducer with a single arc:
#
#  0 -a:@U.x.a@→ (1)
#
# The accepts a single string 'a', transducing it to a flag diacritic.
FST_SOURCE = """##foma-net 1.0##
##props##
2 1 2 3 1 1 1 1 1 1 1 2 34354761
##sigma##
3 @U.x.a@
4 a
##states##
0 3 4 1 0
1 -1 -1 1
-1 -1 -1 -1 -1
##end##
"""


def test_gh021_mismatched_flag_diacritic():
    fst = FST.from_text(FST_SOURCE)
    # The only acceptable string:
    output, = fst.analyze("a")
    # The graphic output of the flag diacritic should a single, emtpy transduction.
    assert output == ()
