import math
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.service import Service
from models.workload import Workload
from resources import game_content
from vars import hardware


class TestGameContent(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_service = mock.MagicMock()
        self.query_workload = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {
            Service: self.query_service,
            Workload: self.query_workload,
        }.__getitem__

    def test__check_exists(self):
        elements = [
            "cpu1",
            "cpu2",
            "gpu1",
            "gpu2",
            "mainboard",
            "ram1",
            "ram2",
            "disk1",
            "disk2",
            "powerPack",
            "case",
            "cooler1",
            "cooler2",
            None,
        ]
        expected_results = [
            {"error": "cpu_not_in_inventory"},
            {"error": "cpu_not_in_inventory"},
            {"error": "gpu_not_in_inventory"},
            {"error": "gpu_not_in_inventory"},
            {"error": "mainboard_not_in_inventory"},
            {"error": "ram_not_in_inventory"},
            {"error": "ram_not_in_inventory"},
            {"error": "disk_not_in_inventory"},
            {"error": "disk_not_in_inventory"},
            {"error": "powerPack_not_in_inventory"},
            {"error": "case_not_in_inventory"},
            {"error": "processorCooler_not_in_inventory"},
            {"error": "processorCooler_not_in_inventory"},
            {},
        ]

        def build_summary_response(missing):
            out = {}
            for element in elements:
                if element == missing:
                    continue
                out[element] = out.get(element, 0) + 1
            return {"elements": out}

        for missing_element, expected_result in zip(elements, expected_results):
            mock.m.contact_microservice.return_value = build_summary_response(missing_element)

            actual_result = game_content.check_exists(
                "super",
                {
                    "cpu": ["cpu1", "cpu2"],
                    "ram": ["ram1", "ram2"],
                    "gpu": ["gpu1", "gpu2"],
                    "disk": ["disk1", "disk2"],
                    "mainboard": "mainboard",
                    "powerPack": "powerPack",
                    "case": "case",
                    "processorCooler": ["cooler1", "cooler2"],
                },
            )

            self.assertEqual((not expected_result, expected_result), actual_result)
            mock.m.contact_microservice.assert_called_with("inventory", ["inventory", "summary"], {"owner": "super"})
            mock.reset_mocks()

    def test__delete_items(self):
        elements = {
            "cpu": ["cpu1", "cpu2"],
            "gpu": ["gpu1", "gpu2"],
            "mainboard": "mainboard",
            "ram": ["ram1", "ram2"],
            "disk": ["disk1", "ssd1"],
            "powerPack": "powerPack",
            "case": "case",
            "processorCooler": ["cooler1"],
        }
        inventory = [
            *elements["cpu"],
            *elements["gpu"],
            elements["mainboard"],
            *elements["ram"],
            *elements["disk"],
            elements["powerPack"],
            elements["case"],
            *elements["processorCooler"],
        ]

        def handle_delete_endpoint(ms, path, data):
            self.assertEqual("inventory", ms)
            self.assertEqual(["inventory", "delete_by_name"], path)
            self.assertEqual("super", data["owner"])
            inventory.remove(data["item_name"])

        mock.m.contact_microservice.side_effect = handle_delete_endpoint

        game_content.delete_items("super", elements)

        self.assertFalse(inventory)

    def test__check_element_existence(self):
        elements = {
            "cpu": [list(hardware["cpu"])[0]],
            "mainboard": list(hardware["mainboard"])[0],
            "gpu": [list(hardware["gpu"])[0]],
            "ram": [list(hardware["ram"])[0]],
            "disk": [list(hardware["disk"])[0]],
            "powerPack": list(hardware["powerPack"])[0],
            "case": list(hardware["case"])[0],
            "processorCooler": [list(hardware["processorCooler"])[0]],
        }

        for e in ["cpu", "mainboard", "gpu", "ram", "disk", "powerPack", "case", "processorCooler"]:
            expected_result = False, {"error": f"element_{e}_not_found"}
            actual_result = game_content.check_element_existence(
                {k: (v if k != e else "does not exist") for k, v in elements.items()}
            )

            self.assertEqual(expected_result, actual_result)

        expected_result = True, {}
        actual_result = game_content.check_element_existence(elements)

        self.assertEqual(expected_result, actual_result)

    def test__generate_scale_with_no_new(self):
        workload = mock.MagicMock()
        workload.performance_cpu = 29
        workload.performance_ram = 23
        workload.performance_gpu = 19
        workload.performance_disk = 17
        workload.performance_network = 13
        workload.usage_cpu = 20
        workload.usage_ram = 30
        workload.usage_gpu = 40
        workload.usage_disk = 0
        workload.usage_network = 50

        expected_result = 1.0, 23 / 30, 19 / 40, 1, 0.26
        actual_result = game_content.generate_scale_with_no_new(workload)

        self.assertEqual(expected_result, actual_result)

    @patch("resources.game_content.generate_scale_with_no_new")
    def test__calculate_real_use(self, gen_scal):
        workload = mock.MagicMock()
        service = mock.MagicMock()
        service.allocated_cpu = 1
        service.allocated_ram = 1
        service.allocated_gpu = 1
        service.allocated_disk = 1
        service.allocated_network = 1

        self.query_workload.get.return_value = workload
        self.query_service.get.return_value = service

        gen_scal.return_value = 1, 2, 3, 4, 5

        expected_result = {"cpu": 1, "ram": 2, "gpu": 3, "disk": 4, "network": 5}
        result = game_content.calculate_real_use("service-uuid")

        self.assertEqual(expected_result, result)
        self.query_service.get.assert_called_with("service-uuid")
        self.query_workload.get.assert_called_with(service.device_uuid)
        gen_scal.assert_called_with(workload)

    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__not_existing(self, cee_patch):
        elements = mock.MagicMock()
        cee_patch.return_value = False, mock.MagicMock()

        expected_result = cee_patch()
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__missing_cpu(self, cee_patch):
        elements = {
            "cpu": [],
            "mainboard": None,
            "gpu": [],
            "disk": [],
            "ram": [],
            "processorCooler": [],
            "powerPack": None,
            "case": None,
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "missing_cpu"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__missing_ram(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": None,
            "gpu": [],
            "disk": [],
            "ram": [],
            "processorCooler": [],
            "powerPack": None,
            "case": None,
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "missing_ram"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__missing_disk(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": None,
            "gpu": [],
            "disk": [],
            "ram": ["ram1"],
            "processorCooler": [],
            "powerPack": None,
            "case": None,
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "missing_disk"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__invalid_amount_of_cpu_coolers(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": None,
            "gpu": [],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1", "cooler2"],
            "powerPack": None,
            "case": None,
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "invalid_amount_of_cpu_coolers"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch("resources.game_content.hardware", {"mainboard": {"mainboard1": {"case": "case1"}}})
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__incompatible_case(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": [],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "incompatible",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "incompatible_case"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {"mainboard": {"mainboard1": {"case": "case1", "graphicUnitOnBoard": None, "power": 10, "cpuSlots": 1}}},
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__not_enough_cpu_slots(self, cee_patch):
        elements = {
            "cpu": ["cpu1", "cpu2"],
            "mainboard": "mainboard1",
            "gpu": [],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1", "cooler2"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "not_enough_cpu_slots"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                }
            },
            "cpu": {"cpu1": {"socket": "incompatible"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__incompatible_cpu_socket(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": [],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "incompatible_cpu_socket"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1"}},
            "processorCooler": {"cooler1": {"socket": "incompatible"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__incompatible_cooler_socket(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": [],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "incompatible_cooler_socket"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__missing_external_gpu(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": [],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "missing_external_gpu"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [{"interface": "int1", "interfaceSlots": 1}],
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__no_compatible_expansion_slot_for_gpu(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1", "gpu1"],
            "disk": ["disk1"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "no_compatible_expansion_slot_for_gpu"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__no_compatible_expansion_slot_for_disk(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2", "disk2"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "no_compatible_expansion_slot_for_disk"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                    "ram": {"ramSlots": 1},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__not_enough_ram_slots(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2"],
            "ram": ["ram1", "ram2"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "not_enough_ram_slots"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                    "ram": {"ramSlots": 1, "ramTyp": []},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
            "ram": {"ram1": {"power": 10, "ramSize": 1337, "ramTyp": "incompatible"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__incompatible_ram_type(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "incompatible_ram_type"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                    "ram": {"ramSlots": 1, "ramTyp": ["typ1"], "frequency": []},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
            "ram": {"ram1": {"power": 10, "ramSize": 1337, "ramTyp": "typ1", "frequency": "incompatible"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__incompatible_ram_frequency(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "incompatible_ram_frequency"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                    "ram": {"ramSlots": 1, "ramTyp": ["typ1"], "frequency": ["freq1"], "maxRamSize": 42},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
            "ram": {"ram1": {"power": 10, "ramSize": 1337, "ramTyp": "typ1", "frequency": "freq1"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__ram_limit_exceeded(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": None,
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "ram_limit_exceeded"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                    "ram": {"ramSlots": 1, "ramTyp": ["typ1"], "frequency": ["freq1"], "maxRamSize": 42},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": None, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
            "ram": {"ram1": {"power": 10, "ramSize": 42, "ramTyp": "typ1", "frequency": "freq1"}},
            "powerPack": {"pack1": {"totalPower": 69}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__insufficient_power_pack(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": "pack1",
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = False, {"error": "insufficient_power_pack"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {
            "mainboard": {
                "mainboard1": {
                    "case": "case1",
                    "graphicUnitOnBoard": None,
                    "power": 10,
                    "cpuSlots": 1,
                    "cpuSocket": "cpu-socket1",
                    "expansionSlots": [
                        {"interface": "int1", "interfaceSlots": 1},
                        {"interface": "int2", "interfaceSlots": 1},
                    ],
                    "diskStorage": {"diskSlots": 1, "interface": "disk-int"},
                    "ram": {"ramSlots": 1, "ramTyp": ["typ1"], "frequency": ["freq1"], "maxRamSize": 42},
                }
            },
            "cpu": {"cpu1": {"socket": "cpu-socket1", "graphicUnit": {}, "power": 10}},
            "processorCooler": {"cooler1": {"socket": "cpu-socket1", "power": 10}},
            "gpu": {"gpu1": {"interface": "int1", "power": 10}},
            "disk": {"disk1": {"power": 10, "interface": "disk-int"}, "disk2": {"power": 10, "interface": "int2"}},
            "ram": {"ram1": {"power": 10, "ramSize": 42, "ramTyp": "typ1", "frequency": "freq1"}},
            "powerPack": {"pack1": {"totalPower": 70}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__successful(self, cee_patch):
        elements = {
            "cpu": ["cpu1"],
            "mainboard": "mainboard1",
            "gpu": ["gpu1"],
            "disk": ["disk1", "disk2"],
            "ram": ["ram1"],
            "processorCooler": ["cooler1"],
            "powerPack": "pack1",
            "case": "case1",
        }
        cee_patch.return_value = True, {}

        expected_result = True, {}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    def test__calculate_power(self):
        elements = {
            "cpu": [list(hardware["cpu"])[0]],
            "mainboard": list(hardware["mainboard"])[0],
            "ram": [list(hardware["ram"])[0]],
            "gpu": [list(hardware["gpu"])[0]],
            "disk": [list(hardware["disk"])[0]],
        }
        cpu = hardware["cpu"][elements["cpu"][0]]
        mainboard = hardware["mainboard"][elements["mainboard"]]
        ram = hardware["ram"][elements["ram"][0]]
        gpu = hardware["gpu"][elements["gpu"][0]]
        disk = hardware["disk"][elements["disk"][0]]

        expected_performance_cpu = cpu["cores"] * cpu["frequencyMax"]
        expected_performance_ram = ram["ramTyp"][1] * (ram["ramSize"] * ram["frequency"]) ** 0.5
        expected_performance_gpu = gpu["ramTyp"][1] * math.sqrt(gpu["ramSize"] * gpu["frequency"])
        expected_performance_disk = 100 * math.log10(disk["writingSpeed"] * disk["readingSpeed"])
        expected_performance_network = mainboard["networkPort"]["speed"]
        actual_result = game_content.calculate_power(elements)

        self.assertEqual(expected_performance_cpu, actual_result[0])
        self.assertEqual(expected_performance_ram, actual_result[1])
        self.assertEqual(expected_performance_gpu, actual_result[2])
        self.assertEqual(expected_performance_disk, actual_result[3])
        self.assertEqual(expected_performance_network, actual_result[4])

    @patch("resources.game_content.Hardware")
    def test__create_hardware(self, hardware_patch):
        elements = {
            "cpu": ["cpu1", "cpu2"],
            "gpu": ["gpu1", "gpu2"],
            "mainboard": "mainboard",
            "ram": ["ram1", "ram2"],
            "disk": ["disk1", "ssd1"],
            "powerPack": "powerPack",
            "case": "case",
            "processorCooler": ["cooler1"],
        }

        def create(device_uuid, element_name, element_type):
            self.assertEqual("my-device", device_uuid)

            if element_type in ("cpu", "gpu", "processorCooler", "ram", "disk"):
                self.assertIn(element_name, elements[element_type])
                elements[element_type].remove(element_name)
                if not elements[element_type]:
                    del elements[element_type]
            else:
                self.assertEqual(element_name, elements[element_type])
                del elements[element_type]

        hardware_patch.create.side_effect = create

        game_content.create_hardware(deepcopy(elements), "my-device")
        self.assertFalse(elements)

    def test__scale_resources(self):
        service = mock.MagicMock()
        service.allocated_cpu = 2
        service.allocated_ram = 3
        service.allocated_gpu = 5
        service.allocated_disk = 7
        service.allocated_network = 11

        game_content.scale_resources([service], (0.9, 0.7, 0.5, 0.3, 0.1))

        mock.m.contact_microservice.assert_called_with(
            "service",
            ["hardware", "scale"],
            {
                "service_uuid": service.service_uuid,
                "cpu": 2 * 0.9,
                "ram": 3 * 0.7,
                "gpu": 5 * 0.5,
                "disk": 7 * 0.3,
                "network": 11 * 0.1,
            },
        )

    def test__generate_scale(self):
        data = 2, 3, 5, 7, 11
        workload = mock.MagicMock()
        workload.performance_cpu = 29
        workload.performance_ram = 23
        workload.performance_gpu = 19
        workload.performance_disk = 17
        workload.performance_network = 13
        workload.usage_cpu = 20
        workload.usage_ram = 30
        workload.usage_gpu = 40
        workload.usage_disk = 0
        workload.usage_network = 50

        expected_result = 1, 23 / 33, 19 / 45, 1, 13 / 61
        actual_result = game_content.generate_scale(data, workload)

        self.assertEqual(expected_result, actual_result)

        workload = mock.MagicMock()
        workload.performance_cpu = 20
        workload.performance_ram = 30
        workload.performance_gpu = 40
        workload.performance_disk = 1
        workload.performance_network = 50
        workload.usage_cpu = 29
        workload.usage_ram = 23
        workload.usage_gpu = 19
        workload.usage_disk = 17
        workload.usage_network = 13

        expected_result = 20 / 31, 1, 1, 1 / 24, 1
        actual_result = game_content.generate_scale(data, workload)

        self.assertEqual(expected_result, actual_result)

    def test__dict2tuple(self):
        data = {}
        expected_result = []
        for k in ["cpu", "ram", "gpu", "disk", "network"]:
            data[k] = k + "_value"
            expected_result.append(data[k])
        expected_result = tuple(expected_result)

        actual_result = game_content.dict2tuple(data)

        self.assertEqual(expected_result, actual_result)

    def test__turn(self):
        data = 1, -2, 3, -4, 5

        expected_result = -1, 2, -3, 4, -5
        actual_result = game_content.turn(data)

        self.assertEqual(expected_result, actual_result)

    def test__stop_all_services(self):
        services = [1, 2, 3, 4]
        self.query_service.filter_by().all.return_value = services.copy()
        workload = mock.MagicMock()
        self.query_workload.get.return_value = workload

        def delete_handler(obj):
            services.remove(obj)

        mock.wrapper.session.delete.side_effect = delete_handler

        game_content.stop_all_service("my-device")
        self.query_service.filter_by.assert_called_with(device_uuid="my-device")
        self.query_workload.get.assert_called_with("my-device")
        self.assertEqual(0, workload.usage_cpu)
        self.assertEqual(0, workload.usage_ram)
        self.assertEqual(0, workload.usage_gpu)
        self.assertEqual(0, workload.usage_disk)
        self.assertEqual(0, workload.usage_network)
        self.assertFalse(services)
        mock.wrapper.session.commit.assert_called_with()

    def test__stop_all_services__delete(self):
        services = [1, 2, 3, 4]
        self.query_service.filter_by().all.return_value = services.copy()
        workload = mock.MagicMock()
        self.query_workload.get.return_value = workload
        services.append(workload)

        def delete_handler(obj):
            services.remove(obj)

        mock.wrapper.session.delete.side_effect = delete_handler

        game_content.stop_all_service("the-device", delete=True)
        self.query_service.filter_by.assert_called_with(device_uuid="the-device")
        self.query_workload.get.assert_called_with("the-device")
        self.assertFalse(services)
        mock.wrapper.session.commit.assert_called_with()
        self.assertEqual(0, workload.usage_cpu)
        self.assertEqual(0, workload.usage_ram)
        self.assertEqual(0, workload.usage_gpu)
        self.assertEqual(0, workload.usage_disk)
        self.assertEqual(0, workload.usage_network)

    def test__stop_services(self):
        game_content.stop_services("some device")
        mock.m.contact_microservice.assert_called_with("service", ["hardware", "stop"], {"device_uuid": "some device"})

    def test__delete_services(self):
        game_content.delete_services("some device")
        mock.m.contact_microservice.assert_called_with(
            "service", ["hardware", "delete"], {"device_uuid": "some device"}
        )
