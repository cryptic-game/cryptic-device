from unittest import TestCase

from resources.game_content import check_compatible
from vars import hardware


class TestVars(TestCase):
    def test__start_pc_compatible(self):
        self.assertEqual((True, {}), check_compatible(hardware["start_pc"]))
