from queue import Queue

from pyflakes_bears.NoFutureImportBear import NoFutureImportBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.settings.Section import Section


class NoFutureImportTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('no_future')
        self.uut = NoFutureImportBear(self.section, Queue())
        self.filename = 'NoFutureImportBearTemp'

    def test_valid(self):
        self.check_validity(self.uut, ['import sys'])
        self.check_validity(self.uut, ['from os import path'])
        self.check_validity(self.uut, ['from ..custom import something'])

    def test_invalid(self):
        self.check_invalidity(self.uut, ['from __future__ import division'])
        self.check_invalidity(self.uut,
                              ['from __future__ import print_function, \\\n',
                               '                       division\n'])
        self.check_invalidity(self.uut,
                              ['from __future__ import division, '
                               'print_function'])
