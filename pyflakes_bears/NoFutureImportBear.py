from coalib.bears.LocalBear import LocalBear
from coalib.results.Result import Result
from coalib.results.Diff import Diff
from pyflakes_bears.PyFlakesASTBear import PyFlakesASTBear
from pyflakes.checker import FutureImportation


class NoFutureImportBear(LocalBear):
    """
    Uses PyFlakesASTBear to remove future imports
    """

    LANGUAGES = {'Python', 'Python 2', 'Python 3'}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    BEAR_DEPS = {PyFlakesASTBear}

    def remove_future_imports(self, file, lineno, corrected_lines):
        """
        Removes all FutureImportation(pyflakes AST) nodes from
        the input line.

        :param file:            The file contents as string array
        :param lineno:          The filename of the file
        :param corrected_lines: A set containing lineno of all violations
                                that have been fixed
        :return:                A tuple containing diff object and
                                corrected_lines
        """
        def handle_backslash(line, lineno, diff, corrected_lines):
            """
            Helper function to handle use of backslash's in import
            statements.

            An example of such statement is:

            `from __future__ import print_function, \\`
            `                       generators`

            :param line:            The content of line in form of str
            :param lineno:          The filename of the file
            :param diff:            A diff object that remanins same until
                                    the logical line is completely removed.
            :param corrected_lines: A set containing lineno of all violations
                                    that have been fixed
            :return:                A tuple containing diff object and
                                    corrected_lines
            """

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
            """
            Helper function to handle use of semicolon in import
            statements.

            An example of such statement is:

            `from __future__ import generators; x = 2`

            :param line:            The content of line in form of str
            :param lineno:          The filename of the file
            :param diff:            A diff object that remanins same until
                                    the logical line is completely removed.
            :param corrected_lines: A set containing lineno of all violations
                                    that have been fixed
            :return:                A tuple containing diff object and
                                    corrected_lines
            """

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
