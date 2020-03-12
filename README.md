python-qdexec
===============

QdExec allows you to Quick and Dirty export python functions
so they can directly be Executed from the shell.

How does it work?
-----------------

Functions to be exported need to:
- supply a signature annotation to indicate how parameters shall be parsed
- return an int
- be registered with a QdExec context

Calling a function is as simple as passing sys.argv to the context.
The context will automatically:
- pick the correct registered function from argv[0]
- parse arguments in the way the function expects
- execute the function
- return its return-value as process exit code
- or print help and error messages on the fly

But why?
--------

Just to explore alternative and shorter ways to write
python-based shell tools.

Minimal example
---------------

Also see `testfun_minimal` and `testfun_simple`.

```

	import QdExec
	executor = QdExec.QdExec()


	@executor.register
	def testfun_minimal(foo: str) -> int:
	    """ function that will echo parameter """
	    print(foo)
	    return 0


	if __name__ == "__main__":
	    executor.exec_argv_exit()

```

Authors
-------

- David R. Piegdon <dgit@piegdon.de>

Licensing
---------

All files are licensed under the LGPL v3.0, see LICENSE.txt .

