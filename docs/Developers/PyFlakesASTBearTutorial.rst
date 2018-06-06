PyFlakes AST Bears
==================

Welcome. This tutorial aims to show you how to use the ``PyFlakesASTBear`` i.e a
metabear which provides with `pyflakes-enhanced-AST
<https://github.com/PyCQA/pyflakes>`__.

Why is This Useful?
-------------------

PyFlakes AST takes care of basic traversing and collection of important nodes. Thus,
saving a whole lot of rework. So, a developer using enhanced AST just needs to work
on the implementation of the new logic that his/her bear provides and need not worry
about the fidelity of the basic node handlers.


What do we Need?
----------------

The only dependency that bear depends on is `pyflakes-enhanced-AST
<https://github.com/PyCQA/pyflakes>`_. This gets already installed with coala-pyflakes.
Howerver if you want to work with some other version of pyflakes you can do install it
as follows:

::

    $ pip3 install pyflakes==<desired-version>

.. note::

    Some versions may break the helper function provided by the metabear.

Writing the Bear
----------------

To write a pyflakes bear you just need to list ``PyFlakesASTBear`` as a dependency bear in
your ``LocalBear``.

.. code:: python

   BEAR_DEPS = {PyFlakesASTBear}


Accessing scopes
----------------

Scopes allows us to analyze a file through various levels. The various
scopes provided by pyflakes are:

-  ModuleScope
-  ClassScopes
-  FunctionScopes
-  GeneratorScopes
-  DoctestScopes

``PyFlakesASTBear`` returns a single object of ``ModuleScope`` however for all
the other scopes a list of objects is returned.


Analyzing results of PyFlakesASTBear
------------------------------------

Consider the following sample code:

.. code:: python

    class Foo:
      class Bar:
        pass

The result returned by ``PyFLakesASTBear`` is as follows:

-  module_scope

   - __len__ = {int} 1
   -  Foo {ClassDefinition}

      -  name = {Str}'Foo'
      -  source = [{ClassDef}]

-  class_scopes

   - 0 = {ClassScope}         # Class scope corresponding to Bar

     - __len__ = {int} 0

   - 1 = {ClassScope}         # Class scope corresponding to Foo

     - __len__ = {int} 1
     - Bar {ClassDefinition}  # This scope contains class Bar

       - name = {Str}'Bar'
       - source = [{ClassDef}]

Writing NoFutureImportBear using PyFlakesASTBear
------------------------------------------------

The NoFutureImportBear will simply detect any occurrence where python
``__future__`` import statement has been used.

Creating the plugin is quite simple. First create a subclass of coalib ``LocalBear``
and then specify ``PyFlakesASTBear`` as a dependency.

.. code:: python

    from pyflakes_bears.PyFlakesASTBear import PyFlakesASTBear

    class NoFutureImportBear(LocalBear):

       BEAR_DEPS = {PyFlakesASTBear}

Now we can use coalib ``dependency_results.get()`` method to fetch the names.
The complete implementation of ``NoFutureImportBear`` looks as follows:

.. code:: python

    class NoFutureImportBear(LocalBear):
      """
      Uses pyflakes-enhance-AST to detect use of future imports
      """
      BEAR_DEPS = {PyFlakesASTBear}

      def run(self, filename, file,
              dependency_results=dict()
              ):
          for result in dependency_results.get(PyFlakesASTBear.name, []):
              for node in result.get_nodes(result.module_scope,
                                           FutureImportation):
                  yield Result.from_values(
                      origin=self,
                      message='Future import %s found' % node.name,
                      file=filename,
                      diffs={filename: corrected},
                      line=node.source.lineno)

As you can see here we used `get_nodes` helper method provided by
``PyFlakesASTBear`` to fetch all nodes of the type ``FutureImportation``
from the ``module_scope``. The ``get_nodes`` method accepts the scope
and the node type and returns all corresponding nodes from the
specified scope.
