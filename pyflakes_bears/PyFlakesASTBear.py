import ast

from coalib.bears.LocalBear import LocalBear
from coalib.results.HiddenResult import HiddenResult
from coalib.results.Result import Result
from pyflakes.checker import Checker
from pyflakes.checker import ClassDefinition, FunctionDefinition
from pyflakes.checker import (ModuleScope, ClassScope, FunctionScope,
                              GeneratorScope, DoctestScope, Argument)


class PyFlakesChecker(Checker):

    def handleNode(self, node, parent):
        if (isinstance(self.scope, (ClassScope, FunctionScope)) and
                not hasattr(self.scope, '_node')):
            self.scope._node = parent
        parent._scope = self.scope
        super().handleNode(node, parent)

    def ARG(self, node):
        self.addBinding(node, Argument(node.arg, node))


class PyFlakesResult(HiddenResult):

    def __init__(self, origin, deadScopes, pyflakes_messages):

        Result.__init__(self, origin, message='')

        self.module_scope = self.get_scopes(ModuleScope, deadScopes)[0]
        self.class_scopes = self.get_scopes(ClassScope, deadScopes)
        self.function_scopes = self.get_scopes(FunctionScope, deadScopes)
        self.generator_scopes = self.get_scopes(GeneratorScope, deadScopes)
        self.doctest_scopes = self.get_scopes(DoctestScope, deadScopes)
        self.pyflakes_messages = pyflakes_messages

    def get_scopes(self, scope_type, scopes):
        return list(filter(lambda scope: type(scope) == scope_type,
                           scopes))

    def get_nodes(self, scope, node_type):
        for _, node in scope.items():
            if type(node) == node_type:
                yield node

    def get_all_nodes(self, scope, node_type, parent=None):
        for _, node in scope.items():
            node.parent = parent
            if type(node) == node_type:
                yield node
            if (hasattr(node.source, '_scope') and
                    isinstance(node, (ClassDefinition, FunctionDefinition))):
                yield from self.get_all_nodes(node.source._scope,
                                              node_type, node)


class PyFlakesASTBear(LocalBear):
    """
    PyFlakesASTBear is a meta bear that generates pyflakes-enhance-AST
    for the input file and provides the results as a HiddenResult object
    to the bear that depends on it.

    Examples of bears that can be constructed using PyFlakesASTBear are:

    -   A NoFutureImportBear that checks a file for use of any `__future__`
        import statement
    -   A PEP8DoctestNamingBear that checks if the python code written in
        docstring follows PEP8 naming convention
    """

    LANGUAGES = {'Python', 'Python 2', 'Python 3'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    def run(self, filename, file):
        tree = ast.parse(''.join(file))
        result = PyFlakesChecker(tree, filename=filename, withDoctest=True)

        yield PyFlakesResult(self, result.deadScopes, result.messages)
