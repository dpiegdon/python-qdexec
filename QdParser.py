
import TypeAnnotations

import inspect
import os
import collections


class QdParser():
    """ The Quick and Dirty shell command parser """

    def __init__(self):
        super().__init__()
        self.registry = collections.OrderedDict()

    def register(self, fun):
        """ force typecasing/checking and register function for shell cmd execution

        register a function as shell command.
        can also be used as a decorator.
        functions are changed to automatically typecast and typecheck parameters
        and the return value where an annotation defines types.
        """
        name = fun.__name__
        fun = TypeAnnotations.parameter_typecast(
                TypeAnnotations.typecheck(
                    TypeAnnotations.returnvalue_typecast(fun)))
        self.registry[name] = fun
        return fun

    def print_help(self, ):
        name_width = 3 + max((len(name) for name in self.registry.keys()))
        print("Available commands:")
        print()
        for name in self.registry:
            command = self.registry[name]
            doc_short = "(no help available)"
            if command.__doc__ is not None:
                doc_short = command.__doc__.lstrip().split("\n")[0]
            print("{} {}".format(command.__name__, inspect.signature(command)))
            print(" " * name_width + doc_short)

    def execute(self, argv):
        # FIXME add handling of '--' to allow passing of generic params to self:
        # things like --help, --verbose, --loglevel x and alike
        # and anything behing '--' is teated as params to fun
        basename = os.path.basename(argv[0])
        params = argv[1:]
        if basename in self.registry:
            command = self.registry[basename]
            try:
                return command(*params)
            except Exception as e:
                print()
                print("Failed to execute command '{}':".format(basename))
                print("{}".format(e))
                print()
                print("{} {}".format(command.__name__, inspect.signature(command)))
                if command.__doc__ is not None:
                    print()
                    print(command.__doc__.lstrip())
                return -1
        else:
            print("Unknown command '{}'!".format(basename))
            print()
            self.print_help()
            return -1

