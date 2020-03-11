#!/usr/bin/python3

import sys
import QdExec


executor = QdExec.QdExec()


@executor.register
def somefun(foo: int, bar: str) -> int:
    """ some random function doing something (tm)

    also this is pretty booooring.
    """
    print("this is the result of <somefun({}, {})>".format(foo, bar))
    return foo


if __name__ == "__main__":
    sys.exit(executor.execute(sys.argv))
