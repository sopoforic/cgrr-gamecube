# Classic Game Resource Reader (CGRR): Parse resources from classic games.
# Copyright (C) 2015  Tracy Poff
#
# This file is part of CGRR.
#
# CGRR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CGRR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CGRR.  If not, see <http://www.gnu.org/licenses/>.
import unittest

import gci

class Test_gamecube_gci_a(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_gci = "test.gci"

    def test_roundtrip(self):
        with open(self.test_gci, "rb") as test_gci:
            original_data = test_gci.read()
        g = gci.read_gci(self.test_gci)
        new_data = gci.write_gci(g)

        self.assertEqual(original_data, new_data,
            "roundtripped gci differs from original")

    def test_get_game_name(self):
        g = gci.read_gci(self.test_gci)

        self.assertEqual(gci.get_game_name(g), "Test Game",
            "game_name read incorrectly")

    def test_get_file_info(self):
        g = gci.read_gci(self.test_gci)

        self.assertEqual(gci.get_file_info(g), "Test file info.",
            "file_info read incorrectly")
