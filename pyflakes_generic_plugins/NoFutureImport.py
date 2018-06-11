from pyflakes.checker import Checker
from pyflakes.checker import ModuleScope
from pyflakes.checker import FutureImportation

__version__ = '0.1'

CODE = 'F482'


class NoFutureImport(object):
    """
    A generic plugin that uses pyflakes AST to detect use of `__future__`
    import in python code.
    """
    name = 'no_future'
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        self._checker = None
        self._module_scope = None

    @property
    def checker(self):
        if self._checker is None:
            self._checker = Checker(self.tree, self.filename)
        return self._checker

    @checker.setter
    def checker(self, checker):
        self._checker = checker

    @property
    def module_scope(self):
        if self._module_scope is None:
            self._module_scope = list(filter(lambda scope:
                                             isinstance(scope,
                                                        ModuleScope),
                                             self.checker.deadScopes))[0]
        return self._module_scope

    def run(self):
        for _, node in self.module_scope.items():
            if isinstance(node, FutureImportation):
                message = ('{code}: Future import {name} found'
                           .format(name=node.name,
                                   code=CODE))
                yield (node.source.lineno, node.source.col_offset,
                       message, NoFutureImport)
