import ast

from coalib.bears.LocalBear import LocalBear
from coalib.results.HiddenResult import HiddenResult
from coalib.results.Result import Result
from pyflakes.checker import Checker
from pyflakes.checker import ClassScope, FunctionScope, ModuleScope
from pyflakes.checker import GeneratorScope, DoctestScope


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
        return list(filter(lambda scope: isinstance(scope, scope_type),
                           scopes))

    def get_nodes(self, scope, node_type):
        for _, node in scope.items():
            if isinstance(node, node_type):
                yield node


class PyFlakesASTBear(LocalBear):
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'

    def run(self, filename, file):
        """
        Generates pyflakes-enhance-AST for the input file and returns
        deadScopes as HiddenResult
        :return:
            One HiddenResult containing a dictionary with keys being
            type of scope and values being a list of scopes generated
            from the file.
        """
        tree = ast.parse(''.join(file))
        result = Checker(tree, filename=filename, withDoctest=True)

        yield PyFlakesResult(self, result.deadScopes, result.messages)
