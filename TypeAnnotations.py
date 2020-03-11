
import decorator
import functools
import inspect


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
                raise ValueError("Failed to typecast parameter {}: {}".format(name, e))
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
            raise ValueError("Failed to typecast return value: {}".format(e))
    return result
