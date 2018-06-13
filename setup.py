#!/usr/bin/env python3

import locale
import os
import platform
import sys
from subprocess import call

import setuptools.command.build_py
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

try:
    lc = locale.getlocale()
    pf = platform.system()
    if pf != 'Windows' and lc == (None, None):
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
except (ValueError, UnicodeError, locale.Error):
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

VERSION = '0.1'

SETUP_COMMANDS = {}


def set_python_path(path):
    if 'PYTHONPATH' in os.environ:
        user_paths = os.environ['PYTHONPATH'].split(os.pathsep)
        user_paths.insert(0, path)
        os.environ['PYTHONPATH'] = os.pathsep.join(user_paths)
    else:
        os.environ['PYTHONPATH'] = path


class PyTestCommand(TestCommand):
    """
    From https://pytest.org/latest/goodpractices.html
    """
    user_options = [('pytest-args=', 'a', 'Arguments to pass to py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


SETUP_COMMANDS['test'] = PyTestCommand


class BuildDocsCommand(setuptools.command.build_py.build_py):

    def initialize_options(self):
        setup_dir = os.path.join(os.getcwd(), __dir__)
        docs_dir = os.path.join(setup_dir, 'docs')
        source_docs_dir = os.path.join(setup_dir, 'docs')

        set_python_path(setup_dir)

        self.apidoc_commands = list()

        self.apidoc_commands.append((
            'sphinx-apidoc', '-f', '-o', source_docs_dir,
            os.path.join(setup_dir, 'pyflakes_bears')
        ))

        self.apidoc_commands.append((
            'sphinx-apidoc', '-f', '-o', source_docs_dir,
            os.path.join(setup_dir, 'pyflakes_generic_plugins')
        ))

        self.make_command = (
            'make', '-C',
            docs_dir,
            'html', 'SPHINXOPTS=-W',
        )

        # build_lib & optimize is set to these as a
        # work around for "AttributeError"
        self.build_lib = ''
        self.optimize = 2

    def run(self):
        for command in self.apidoc_commands:
            err_no = call(command)
            if err_no:
                sys.exit(err_no)
        err_no = call(self.make_command)
        sys.exit(err_no)


SETUP_COMMANDS['docs'] = BuildDocsCommand

__dir__ = os.path.dirname(__file__)
filename = os.path.join(__dir__, 'requirements.txt')
with open(filename) as requirements:
    required = requirements.read().splitlines()

filename = os.path.join(__dir__, 'test-requirements.txt')
with open(filename) as requirements:
    test_required = requirements.read().splitlines()

filename = os.path.join(__dir__, 'README.rst')
with open(filename) as readme:
    long_description = readme.read()

extras_require = None
EXTRAS_REQUIRE = {}
data_files = None

if extras_require:
    EXTRAS_REQUIRE = extras_require
SETUP_COMMANDS.update({
})

if __name__ == '__main__':
    setup(name='coala-pyflakes',
          version=VERSION,
          description='A collection of bears implemented using pyflakes-enhanced-AST',
          author='Ankit Joshi',
          author_email='ajankit2304@gmail.com',
          maintainer='Lasse Schuirmann, Fabian Neuschmidt, Mischa Kr\xfcger',
          maintainer_email=('lasse.schuirmann@gmail.com, '
                            'fabian@neuschmidt.de, '
                            'makman@alice.de'),
          url='https://github.com/macbox7/coala-pyflakes',
          platforms='any',
          packages=find_packages(exclude=('build.*', 'tests', 'tests.*')),
          install_requires=required,
          extras_require=EXTRAS_REQUIRE,
          tests_require=test_required,
          package_data={'pyflakes_bears': ['VERSION']},
          license='MIT',
          data_files=data_files,
          long_description=long_description,
          # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=[
              'Development Status :: 4 - Beta',

              'Environment :: Console',
              'Environment :: MacOS X',
              'Environment :: Win32 (MS Windows)',

              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',

              'License :: OSI Approved :: MIT License'

              'Operating System :: OS Independent',

              'Programming Language :: Python :: Implementation :: CPython',
              'Programming Language :: Python :: 3.4',
              'Programming Language :: Python :: 3.5',
              'Programming Language :: Python :: 3.6',
              'Programming Language :: Python :: 3 :: Only',

              'Topic :: Scientific/Engineering :: Information Analysis',
              'Topic :: Software Development :: Quality Assurance',
              'Topic :: Text Processing :: Linguistic'],
          cmdclass=SETUP_COMMANDS,
          )
