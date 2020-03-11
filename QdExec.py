
import TypeAnnotations

import inspect
import os
import collections
import logging


class QdExec():
    """ The Quick and Dirty command Executor """

    def __init__(self, logger_name=None):
        super().__init__()
        self.registry = collections.OrderedDict()
        self.logger = logging.getLogger(logger_name)

    def get_logger(self):
        return self.logger

    def register(self, fun):
        """ force typecasing/checking and register function for command execution

        register a function as command.
        can also be used as a decorator.
        functions are changed to automatically typecast and typecheck
        parameters and the return value where an annotation defines types.
        """
        name = fun.__name__
        fun = TypeAnnotations.parameter_typecast(
                TypeAnnotations.typecheck(
                    TypeAnnotations.returnvalue_typecast(fun)))
        self.registry[name] = fun
        return fun

    def print_help(self):
        """ print help on all registered commands """
        name_width = 3 + max((len(name) for name in self.registry.keys()))
        self.logger.warning("Available commands:")
        self.logger.warning("")
        for name in self.registry:
            command = self.registry[name]
            doc_short = "(no help available)"
            if command.__doc__ is not None:
                doc_short = command.__doc__.lstrip().split("\n")[0]
            self.logger.warning("{} {}".format(command.__name__,
                                               inspect.signature(command)))
            self.logger.warning(" " * name_width + doc_short)

    def print_command_help(self, commandname):
        """ print help on specified command """
        command = self.registry[commandname]
        self.logger.warning("{} {}".format(command.__name__,
                            inspect.signature(command)))
        if command.__doc__ is not None:
            self.logger.warning("")
            self.logger.warning(command.__doc__.lstrip())

    def print_long_help(self):
        """ print long help on all registered commands """
        self.logger.warning("Available commands:")
        for name in self.registry:
            self.logger.warning("")
            self.print_command_help(name)

    def execute(self, argv, reduced_basename=True):
        """ find and execute command with given arguments

        find command @argv[0] in registry and execute it with the remaining
        arguments.
        if @reduced_basename, the basename is searched instead.
        if command was not registered, an appropriate help and
        all registered commands with short description (first line of
        docstring) is listed.
        if command fails to execute, appropriate help and a proper description
        of the command (full docstring) is listed.
        """
        # FIXME add handling of '--' to allow passing of
        # generic params to self:
        # things like --help, --verbose, --loglevel x and alike
        # and anything behing '--' is teated as params to fun
        commandname = argv[0]
        if reduced_basename:
            commandname = os.path.basename(commandname)

        params = argv[1:]
        if commandname in self.registry:
            command = self.registry[commandname]
            try:
                return command(*params)
            except Exception as e:
                self.logger.error("ERROR: {}".format(e))
                self.logger.error("Failed to execute '" + commandname + "'.")
                self.logger.error("")
                self.print_command_help(commandname)
                return -1
        else:
            self.logger.error("Unknown command '{}'!".format(commandname))
            self.logger.error("")
            self.print_help()
            return -1
