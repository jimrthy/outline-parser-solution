#! /usr/bin/env pytest

import script


def test_bullet_nesting():
    input = """* This is an outline

. It's not a very good outline

.. I've seen better

.. I've seen worse

... I saw a really bad one back in 2008
    """
    parser = script.TreeBuilder()
    #breakpoint()
    for line in input.split('\n'):
        parser.parse(line)

    actual = str(parser)
    expected = """1 This is an outline
  + It's not a very good outline
   - I've seen better
   + I've seen worse
    - I saw a really bad one back in 2008
"""
    assert expected == actual
