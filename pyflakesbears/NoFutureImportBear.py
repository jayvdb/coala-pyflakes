from coalib.bears.LocalBear import LocalBear
from coalib.results.Result import Result
from pyflakesbears.PyFlakesASTBear import PyFlakesASTBear
from pyflakes.checker import FutureImportation


class NoFutureImportBear(LocalBear):
    """
    Uses pyflakes-enhance-AST to detect use of future imports
    """
    LANGUAGES = {'Python', 'Python 2', 'Python 3'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
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
                    line=node.source.lineno)
