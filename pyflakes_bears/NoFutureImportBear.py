from coalib.bears.LocalBear import LocalBear
from coalib.results.Result import Result
from coalib.results.Diff import Diff
from pyflakes_bears.PyFlakesASTBear import PyFlakesASTBear
from pyflakes.checker import FutureImportation


class NoFutureImportBear(LocalBear):
    """
    Uses pyflakes-enhance-AST to remove future imports
    """

    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    BEAR_DEPS = {PyFlakesASTBear}

    def remove_future_imports(self, file, lineno, corrected_lines):
        """
        Removes all ImportFrom nodes from the input line
        """
        def handle_backslash(line, lineno, diff, corrected_lines):
            corrected_lines.add(lineno)
            semicolon_index = line.find(';')
            if semicolon_index == -1:
                if line.rstrip()[-1] == '\\':
                    next_line = file[lineno]
                    diff, corrected_lines = handle_backslash(
                        next_line, lineno+1, diff, corrected_lines)
                diff.delete_line(lineno)
            else:
                replacement = line[semicolon_index + 1:].lstrip()
                diff, corrected_lines = handle_semicolon(
                    replacement, lineno, diff, corrected_lines)

            return diff, corrected_lines

        def handle_semicolon(line, lineno, diff, corrected_lines):
            corrected_lines.add(lineno)
            if not line.lstrip().startswith('from __future__'):
                return diff, corrected_lines
            semicolon_index = line.find(';')
            if semicolon_index == -1:
                diff, corrected_lines = handle_backslash(
                    line, lineno, diff, corrected_lines)
            else:
                replacement = line[semicolon_index + 1:].lstrip()
                diff.modify_line(lineno, replacement)
                if len(replacement) != 0:
                    diff, corrected_lines = handle_semicolon(
                        replacement, lineno, diff, corrected_lines)

            return diff, corrected_lines

        diff = Diff(file)
        line = file[lineno - 1]
        diff, corrected_lines = handle_semicolon(
            line, lineno, diff, corrected_lines)

        return diff, corrected_lines

    def run(self, filename, file,
            dependency_results=dict()
            ):
        """
        Uses PyFlakesASTBear to get only FutureImportation
        """
        corrected_lines = set()
        for result in dependency_results.get(PyFlakesASTBear.name, []):
            for node in result.get_nodes(result.module_scope,
                                         FutureImportation):
                lineno = node.source.lineno
                if lineno not in corrected_lines:
                    corrected, corrected_lines = self.remove_future_imports(
                                file, lineno, corrected_lines
                                )
                    yield Result.from_values(
                        origin=self,
                        message='Future import(s) found',
                        file=filename,
                        diffs={filename: corrected},
                        line=lineno)
