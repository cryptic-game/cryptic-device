from unittest import TestCase

from resources.game_content import check_compatible
from vars import hardware


class TestVars(TestCase):
    def test__start_pc_compatible(self):
        self.assertEqual((True, {}), check_compatible(hardware["start_pc"]))

    def test__config__mainboard(self):
        for name, mainboard in hardware["mainboard"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(mainboard["case"], str)
            self.assertIsInstance(mainboard["cpuSocket"], str)
            self.assertIsInstance(mainboard["cpuSlots"], int)
            self.assertGreaterEqual(mainboard["cpuSlots"], 1)

            self.assertIsInstance(mainboard["ram"]["ramSlots"], int)
            self.assertGreaterEqual(mainboard["ram"]["ramSlots"], 1)
            self.assertIsInstance(mainboard["ram"]["maxRamSize"], int)
            self.assertGreaterEqual(len(mainboard["ram"]["ramTyp"]), 1)
            for interface, version in mainboard["ram"]["ramTyp"]:
                self.assertIsInstance(interface, str)
                self.assertIsInstance(version, int)
            self.assertGreaterEqual(len(mainboard["ram"]["frequency"]), 1)
            for frequency in mainboard["ram"]["frequency"]:
                self.assertIsInstance(frequency, int)

            if mainboard["graphicUnitOnBoard"] is not None:
                self.assertIsInstance(mainboard["graphicUnitOnBoard"]["name"], str)
                self.assertIsInstance(mainboard["graphicUnitOnBoard"]["ramSize"], int)
                self.assertIsInstance(mainboard["graphicUnitOnBoard"]["frequency"], int)

            for slot in mainboard["expansionSlots"]:
                self.assertIsInstance(slot["interface"][0], str)
                self.assertIsInstance(slot["interface"][1], int)
                self.assertIsInstance(slot["interfaceSlots"], int)
                self.assertGreaterEqual(slot["interfaceSlots"], 1)

            self.assertIsInstance(mainboard["diskStorage"]["diskSlots"], int)
            self.assertGreaterEqual(mainboard["diskStorage"]["diskSlots"], 1)
            for interface, version in mainboard["diskStorage"]["interface"]:
                self.assertIsInstance(interface, str)
                self.assertIsInstance(version, int)

            self.assertIsInstance(mainboard["power"], int)

    def test__config__cpu(self):
        for name, cpu in hardware["cpu"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(cpu["frequencyMin"], int)
            self.assertIsInstance(cpu["frequencyMax"], int)
            self.assertLessEqual(cpu["frequencyMin"], cpu["frequencyMax"])
            self.assertIsInstance(cpu["socket"], str)
            self.assertIsInstance(cpu["cores"], int)
            self.assertGreaterEqual(cpu["cores"], 1)

            if cpu["graphicUnit"] is not None:
                self.assertIsInstance(cpu["graphicUnit"]["name"], str)
                self.assertIsInstance(cpu["graphicUnit"]["ramSize"], int)
                self.assertIsInstance(cpu["graphicUnit"]["frequency"], int)

            self.assertIsInstance(cpu["power"], int)

    def test__config__cpu_cooler(self):
        for name, cooler in hardware["processorCooler"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(cooler["socket"], str)
            self.assertIsInstance(cooler["power"], int)

    def test__config__ram(self):
        for name, ram in hardware["ram"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(ram["ramSize"], int)
            self.assertIsInstance(ram["ramTyp"][0], str)
            self.assertIsInstance(ram["ramTyp"][1], int)
            self.assertIsInstance(ram["frequency"], int)
            self.assertIsInstance(ram["power"], int)

    def test__config__gpu(self):
        for name, gpu in hardware["gpu"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(gpu["ramSize"], int)
            self.assertIsInstance(gpu["ramTyp"][0], str)
            self.assertIsInstance(gpu["ramTyp"][1], int)
            self.assertIsInstance(gpu["frequency"], int)
            self.assertIsInstance(gpu["interface"][0], str)
            self.assertIsInstance(gpu["interface"][1], int)
            self.assertIsInstance(gpu["power"], int)

    def test__config__disk(self):
        for name, disk in hardware["disk"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(disk["capacity"], int)
            self.assertIsInstance(disk["writingSpeed"], int)
            self.assertIsInstance(disk["readingSpeed"], int)
            self.assertIsInstance(disk["interface"][0], str)
            self.assertIsInstance(disk["interface"][1], int)
            self.assertIsInstance(disk["power"], int)

    def test__config__power_pack(self):
        for name, power_pack in hardware["powerPack"].items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(power_pack["totalPower"], int)

    def test__config__case(self):
        for name in hardware["case"]:
            self.assertIsInstance(name, str)
