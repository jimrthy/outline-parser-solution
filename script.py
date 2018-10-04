#! /usr/bin/env python

"""
This is written using some python 3.7 features
"""

import collections
import re
import sys

BULLET_TAG = '.'
ORDERED_TAG = '*'

TAG_EXTRACTOR = re.compile(r'\s')


class Outliner:
    """
    Track the state of the outline and transform each line
    """
    def __init__(self):
        dispatcher = {
            BULLET_TAG: self.bullet_point,
            ORDERED_TAG: self.numbered_point
        }

        def continuation():
            return self.continuation

        self.dispatcher = collections.defaultdict(continuation,
                                                  dispatcher)

        # Each element of the list indicates the current nesting level
        self.number_nesting = [0]
        # How far do we indent bulleted lists and continuation lines?
        # Note that continuation lines get an extra 2 spaces
        self.unordered_indentation = 0

    def bullet_point(self, tag: str, body: str) -> str:
        """
        Like an ul in html

        Args:
            tag: Shows indentation level
            body: Line to process
        Returns: processed output
        """
        self.unordered_indentation = len(tag) + 1
        indentation = ' ' * self.unordered_indentation
        # This is supposed to alternate between + and -, but I don't
        # see any rhyme or reason to it yet.
        bullet = '+'
        return f'{indentation}{bullet} {body}'

    def continuation(self, first_word: str, remainder: str) -> str:
        """
        Continue the previous outline level

        Args:
            first_word: Start of line
            remainder: Rest of line
        Returns: processed output
        """
        #print(f'==Continuing: "{first_word}" and "{remainder}"')
        indentation = ' ' * (self.unordered_indentation + 2)
        result = f'{indentation}{first_word} {remainder}'
        return result

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

        return f'{prefix} {body}'

    def parse(self, line):
        """
        Handle the next line of input
        """
        tag, body = re.split(TAG_EXTRACTOR, line, 1)
        if tag:
            symbol = tag[0]
            if symbol in {BULLET_TAG, ORDERED_TAG}:
                for character in tag[1:]:
                    if character != tag[0]:
                        # This is undefined, but seems safer than ignoring
                        # the problem
                        raise ValueError(tag)
            processor = self.dispatcher[symbol]
            result = processor(tag, body)
            # FIXME: debug only
            #print(f'Processing:\n"{line}"\nwith: {processor} Result:\n"{result}"')
            return result


def main(argv):
    outliner = Outliner()

    for line in sys.stdin:
        output = outliner.parse(line)
        if output:
            print(output, end='')


if __name__ == '__main__':
    main(sys.argv)
