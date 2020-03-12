
import TypeAnnotations

import collections
import inspect
import logging
import os


class QdExec():
    """ The Quick and Dirty command Executor """
    InternalParam = collections.namedtuple("InternalParam",
                                           ["callback", "help"])
    # callback must be a callable that gets the commandname and
    # *all* further parameters as a list, and returns those parameters
    # not consumed as a list

    def __init__(self, logger_name=None, logger_format="%(message)s"):
        """ init executor

        executor will use given logger and initialise the logging system
        with given logging format. (ignored if logger was initialized before)
        """
        super().__init__()
        self.registry = collections.OrderedDict()
        self.logger = logging.getLogger(logger_name)
        self.logger_format = logger_format

        self.internal_params = {}

        def LogLevelParam(name, level):
            def LogLevelSetter(commanename, args):
                self.loglevel = level
                return args
            return self.InternalParam(LogLevelSetter, "set loglevel to "+name)
        for name, level in [("critical", logging.CRITICAL),
                            ("error", logging.ERROR),
                            ("warning", logging.WARNING),
                            ("info", logging.INFO),
                            ("debug", logging.DEBUG)]:
            self.internal_params["--"+name] = LogLevelParam(name, level)

        def HelpParamParser(commandname, args):
            if (len(args) > 0 and
                    ("--" not in args[0] or args[0].index("--") != 0)):
                command = args.pop(0)
                self.print_command_help(command)
            else:
                if commandname in self.registry:
                    self.print_command_help(commandname)
                else:
                    self.logger.error("unknown command: "+commandname)
                    self.logger.error("")
                    self.print_help()
            return None
        helpcmd = self.InternalParam(HelpParamParser,
                                     "show help, optionally for command given")
        self.internal_params["--help"] = helpcmd

        def LongHelpParamParser(commandname, args):
            self.print_long_help()
            return None
        longhelpcmd = self.InternalParam(LongHelpParamParser, "show long help")
        self.internal_params["--longhelp"] = longhelpcmd

    def parse_internal_params(self, commandname, params):
        """ parse any internal parameters

        we don't rely on argparse here as argparse is very aggressive with
        direct user interaction. """
        self.loglevel = logging.INFO

        while len(params):
            param = params[0]
            if param in self.internal_params:
                params = self.internal_params[param].callback(commandname, params[1:])
                if params is None:
                    return False
            else:
                break

        logging.basicConfig(format=self.logger_format, level=self.loglevel)
        self.logger.setLevel(self.loglevel)
        self.logger.debug("loglevel set to {}".format(self.loglevel))

        if len(params) > 0:
            raise TypeError("unknown internal parameter(s): {}".format(params))

        return True

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

    def print_internal_help(self):
        """ print help on all available internal parameters """
        self.logger.warning("Expected parameters:")
        self.logger.warning("    [<internal parameters> --] [command parameters]")
        self.logger.warning("")
        self.logger.warning("available internal parameters:")
        for iparam in self.internal_params:
            self.logger.warning("    {}: {}".format(iparam, self.internal_params[iparam].help))

    def print_help(self):
        """ print help on all registered commands """
        self.print_internal_help()
        self.logger.warning("")
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
        if commandname in self.registry:
            command = self.registry[commandname]
            self.logger.warning("{} {}".format(command.__name__,
                                inspect.signature(command)))
            if command.__doc__ is not None:
                self.logger.warning("")
                self.logger.warning(command.__doc__)
        else:
            self.logger.warning("unknown command: "+commandname)

    def print_long_help(self):
        """ print long help on all registered commands """
        self.print_internal_help()
        self.logger.warning("")
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
        commandname = argv[0]
        if reduced_basename:
            commandname = os.path.basename(commandname)

        params = argv[1:]

        if "--" in params:
            try:
                split = params.index("--")
                internal_params = params[:split]
                params = params[split+1:]
                if not self.parse_internal_params(commandname, internal_params):
                    return -1
            except TypeError as e:
                # early abort due to internal parameters
                print("ERROR: {}".format(e))
                return -1

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
