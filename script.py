#! /usr/bin/env python

import sys

class Outliner:
    def __init__(self):
        pass

    def parse(line):
        return line

def main(argv):
    outliner = Outliner()

    for line in sys.stdin:
        output = outliner.parse(line)
        if output:
            print(output, end='')

if __name__ == '__main__':
    main(sys.argv)
