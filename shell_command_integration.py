#!/usr/bin/python3

import decorator
import functools
import inspect
import sys
import os


@decorator.decorator
def typecheck(fun, *args, **kwargs):
    """ typecheck parameters and return value while executing function

    check parameter types for given function and parameters based on the
    functions signature annotations; execute function; check return type as
    well. raises TypeError on any mismatch.
    types are checked where defined. undefined types are not checked.
    """
    # check parameters
    for name, val in inspect.getcallargs(fun, *args, **kwargs).items():
        if name in fun.__annotations__:
            if not isinstance(val, fun.__annotations__[name]):
                raise TypeError("Expected argument "
                                + "'{}' of type {} but got {}.".format(
                                    name, fun.__annotations__[name], type(val)))
    # call wrapped function
    result = fun(*args, **kwargs)
    # check return value
    if "return" in fun.__annotations__:
        if not isinstance(result, fun.__annotations__["return"]):
            raise TypeError("Expected return of type "
                            + "{} but got {}.".format(
                                   fun.__annotations__["return"], type(result)))
    # return result from wrapped function
    return result


@decorator.decorator
def parameter_typecast(fun, *args, **kwargs):
    """ typecast parameter before executing function

    before executing the given function, all parameters are typecasted to
    the type defined in the functions signature annotation.
    if no type is defined, no typecast is done.
    """
    original_args = inspect.getcallargs(fun, *args, **kwargs).items()
    casted_args = {}
    annotations = fun.__annotations__
    for name, val in original_args:
        if (name in annotations and not isinstance(val, annotations[name])):
            try:
                casted_args[name] = annotations[name](val)
            except ValueError as e:
                raise TypeError("Failed to typecast parameter {}: {}".format(name, e))
        else:
            casted_args[name] = val
    return fun(**casted_args)


@decorator.decorator
def returnvalue_typecast(fun, *args, **kwargs):
    """ typecast return value after executing function

    after executing the given function, the return value is typecasted to the
    type defined in the functions signature annotation.
    if no type is defined, no typecast is done.
    """
    annotations = fun.__annotations__
    result = fun(*args, **kwargs)
    if "return" in annotations and not isinstance(
            result, annotations["return"]):
        try:
            result = annotations["return"](result)
        except ValueError as e:
            raise TypeError("Failed to typecast return value: {}".format(e))
    return result


shell_command_registry = {}
def register_as_shell_command(fun):
    """ register a function for shell command execution

    register a function or shell command into the given context.
    can also be used as a decorator. """
    shell_command_registry[fun.__name__] = fun
    return fun


def execute_shell_command(argv):
    # FIXME add handling of '--' to allow passing of generic params to self:
    # things like --help, --verbose, --loglevel x and alike
    # and anything behing '--' is teated as params to fun
    basename = os.path.basename(argv[0])
    params = argv[1:]
    if basename in shell_command_registry:
        command = shell_command_registry[basename]
        try:
            sys.exit(command(*params))
        except Exception as e:
            print()
            print("Failed to execute command '{}':".format(basename))
            print("{}".format(e))
            print()
            print("{} {}".format(command.__name__, inspect.signature(command)))
            if command.__doc__ is not None:
                print()
                print(command.__doc__.lstrip())
            sys.exit(-1)
    else:
        name_width = 3 + max((len(name) for name in shell_command_registry.keys()))
        print("Unknown command '{}'!".format(basename))
        print()
        print("Available commands:")
        print()
        for name in shell_command_registry:
            command = shell_command_registry[name]
            doc_short = "(no help available)"
            if command.__doc__ is not None:
                doc_short = command.__doc__.lstrip().split("\n")[0]
            print("{} {}".format(command.__name__, inspect.signature(command)))
            print(" " * name_width + doc_short)
        sys.exit(-1)


@register_as_shell_command
@parameter_typecast
@typecheck
@returnvalue_typecast
def somefun(foo: int, bar: str) -> int:
    """ some random function doing something (tm)"""
    print("this is the result of <somefun({}, {})>".format(foo, bar))
    return foo


if __name__ == "__main__":
    execute_shell_command(sys.argv)
