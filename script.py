#! /usr/bin/env python

"""
This is written using some python 3.7 features
"""

import collections
import re
import sys

BULLET_TAG = '.'
# The rule for which bullet to use seems to depend on whether there's
# increased nesting below it.
FLAT_BULLET = '-'
NEST_BULLET = '+'
ORDERED_TAG = '*'

TAG_EXTRACTOR = re.compile(r'\s')


class TreeBuilder:
    """
    Build up the outline in memory
    """
    def __init__(self):
        dispatcher = {
            BULLET_TAG: self.bullet_point,
            ORDERED_TAG: self.numbered_point
        }

        # This is awkward, but the default dict balances that
        def continuation():
            return self.continuation

        self.dispatcher = collections.defaultdict(continuation,
                                                  dispatcher)

        # Each element of the list indicates the current nesting level
        self.number_nesting = [0]
        # How far do we indent bulleted lists and continuation lines?
        # Note that continuation lines get an extra 2 spaces
        self.unordered_indentation = 0

        # For large data sets, this gets more complicated because it
        # would really need to be stored on disk.
        # That isn't a concern yet, but it could very well turn into
        # one quickly.
        self.parse_tree = []

    def cope_with_bullet_nesting(self, tag: str) -> str:
        """
        Updates indentation and possibly the parent bullet style

        Args:
            tag: Tells us the indentation level for the current line

        Returns: Meaningless. Called for side-effects.
        """
        # For large data sets, there's a good chance that this
        # would make more sense as a second pass parser.
        next_ul_indent = len(tag) + 1
        if next_ul_indent > self.unordered_indentation:
            # Search lines back from the most recent.
            # Have to skip over continuations
            previous = len(self.parse_tree) - 1
            # This is almost obnoxious enough to convince me to use
            # a data class instead of a plain pair.
            while self.parse_tree[previous][0][-1] == ' ':
                previous -= 1
                if previous < 0:
                    break
            if previous >= 0 and \
               self.parse_tree[previous][0][-1] == FLAT_BULLET:
                replacement = (f'{self.parse_tree[previous][0][:-1]}'
                               f'{NEST_BULLET}')
                self.parse_tree[previous][0] = replacement
        self.unordered_indentation = next_ul_indent

    def bullet_point(self, tag: str, body: str) -> str:
        """
        Like an ul in html

        Args:
            tag: Shows indentation level
            body: Line to process
        Returns: processed output
        """
        self.cope_with_bullet_nesting(tag)
        indentation = ' ' * self.unordered_indentation
        return [f'{indentation}{FLAT_BULLET}', body]

    def continuation(self, first_word: str, remainder: str) -> str:
        """
        Continue the previous outline level

        Args:
            first_word: Start of line
            remainder: Rest of line
        Returns: processed output
        """
        indentation = ' ' * (self.unordered_indentation + 1)
        return (indentation, f'{first_word} {remainder}')

    def increment_numbering(self, tag: str) -> str:
        """
        Go to the next number for the outline

        Increased indentation levels take on deeper levels of nesting.

        e.g.
        1
        1.1
        1.2
        1.2.1
        1.3
        1.3.1
        1.3.1.1


        Args:
            tag: Controls the depth of nesting
        Returns: Next section number
        """
        nesting = len(tag)
        current = len(self.number_nesting)
        if nesting == current:
            pass
        elif nesting < current:
            self.number_nesting = self.number_nesting[:nesting]
        else:
            for _ in range(nesting - current - 1):
                # Spec doesn't define what to do if the input skips
                # nesting levels. This seems like the most reasonable
                # option
                self.number_nesting.append(1)
            self.number_nesting.append(0)
        self.number_nesting[-1] += 1
        return '.'.join(map(str, self.number_nesting))

    def numbered_point(self, tag: str, body: str) -> str:
        """
        Basically like an ol in html

        Args:
            tag: Shows indentation level
            body: Line to process
        Returns: processed output
        """
        prefix = self.increment_numbering(tag)

        return (prefix, body)

    def parse(self, line: str):
        """
        Add another line of input to the parsed tree

        Returns: Meaningless. Called for side-effects
        """
        line = line.strip()
        if line:
            try:
                tag, body = re.split(TAG_EXTRACTOR, line, 1)
            except TypeError as ex:
                print(f'{ex}\nTrying to split {line}')
            if tag:
                symbol = tag[0]
                if symbol in {BULLET_TAG, ORDERED_TAG}:
                    for character in tag[1:]:
                        if character != symbol:
                            # This is undefined, but seems safer than ignoring
                            # the problem
                            raise ValueError(tag)
                processor = self.dispatcher[symbol]
                result = processor(tag, body)
                self.parse_tree.append(result)

    def __str__(self) -> str:
        """
        Converts a ParseTree into a string
        """
        result = ''
        for prefix, body in self.parse_tree:
            result += f'{prefix} {body}\n'
        # The final newline isn't in the spec either way. It would be
        # trivial to strip it for correctness.
        return result


def main(argv):
    parser = TreeBuilder()

    for line in sys.stdin:
        parser.parse(line)

    print(str(parser))


if __name__ == '__main__':
    main(sys.argv)
