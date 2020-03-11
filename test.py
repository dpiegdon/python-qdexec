#!/usr/bin/python3

import sys
import QdParser


parser = QdParser.QdParser()


@parser.register
def somefun(foo: int, bar: str) -> int:
    """ some random function doing something (tm)"""
    print("this is the result of <somefun({}, {})>".format(foo, bar))
    return foo


if __name__ == "__main__":
    sys.exit(parser.execute(sys.argv))
