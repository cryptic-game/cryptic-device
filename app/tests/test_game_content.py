import math
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.service import Service
from models.workload import Workload
from resources import game_content
from vars import hardware, resolve_ram_type, resolve_gpu_type


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
        elements = ["cpu", "gpu", "motherboard", "ram1", "ram2", "disk1", None]
        expected_results = [
            {"error": "you_dont_own_such_cpu"},
            {"error": "you_dont_own_such_gpu"},
            {"error": "you_dont_own_such_motherboard"},
            {"error": "you_dont_own_such_ram"},
            {"error": "you_dont_own_such_ram"},
            {"error": "you_dont_own_such_disk"},
            {},
        ]

        for missing_element, expected_result in zip(elements, expected_results):
            mock.m.contact_microservice.return_value = {
                "elements": [{"element_name": e} for e in elements if e != missing_element]
            }

            actual_result = game_content.check_exists(
                "super",
                {"cpu": "cpu", "ram": ["ram1", "ram2"], "gpu": "gpu", "disk": ["disk1"], "motherboard": "motherboard"},
            )

            self.assertEqual((not expected_result, expected_result), actual_result)
            mock.m.contact_microservice.assert_called_with("inventory", ["inventory", "list"], {"owner": "super"})
            mock.reset_mocks()

    def test__delete_items(self):
        elements = {
            "cpu": "cpu",
            "gpu": "gpu",
            "motherboard": "motherboard",
            "ram": ["ram1", "ram2"],
            "disk": ["disk1", "ssd1"],
        }
        inventory = [elements["cpu"], elements["gpu"], elements["motherboard"], *elements["ram"], *elements["disk"]]

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
            "cpu": list(hardware["cpu"])[0],
            "motherboard": list(hardware["mainboards"])[0],
            "gpu": list(hardware["gpu"])[0],
            "ram": [list(hardware["ram"])[0]],
            "disk": [list(hardware["disk"])[0]],
        }

        for e in ["cpu", "motherboard", "gpu", "ram", "disk"]:
            expected_result = False, {"error": f"element_{e}_not_found"}
            actual_result = game_content.check_element_existence(
                {k: (v if k != e else "does not exist") for k, v in elements.items()}
            )

            self.assertEqual(expected_result, actual_result)

        expected_result = True, {}
        actual_result = game_content.check_element_existence(elements)

        self.assertEqual(expected_result, actual_result)

    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__not_existing(self, cee_patch):
        elements = mock.MagicMock()
        cee_patch.return_value = False, mock.MagicMock()

        expected_result = cee_patch()
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)
        cee_patch.assert_called_with(elements)

    @patch(
        "resources.game_content.hardware",
        {"cpu": {"cpu": {"sockel": "foo"}}, "mainboards": {"motherboard": {"sockel": "bar"}}},
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__sockel_does_not_fit(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": None, "disk": None}

        expected_result = False, {"error": "cpu_and_mainboard_sockel_do_not_fit"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    @patch(
        "resources.game_content.hardware",
        {"cpu": {"cpu": {"sockel": "foo"}}, "mainboards": {"motherboard": {"sockel": "foo", "ram": {"ramSlots": 2}}}},
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__not_enough_ram_slots(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": ["ram1", "ram2", "ram3", "ram4"], "disk": None}

        expected_result = False, {"error": "mainboard_has_not_this_many_ram_slots"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    @patch(
        "resources.game_content.hardware",
        {
            "cpu": {"cpu": {"sockel": "foo"}},
            "mainboards": {"motherboard": {"sockel": "foo", "ram": {"ramSlots": 2, "typ": "xyz"}}},
            "ram": {"ram": {"ramTyp": "abc"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__ram_does_not_fit(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": ["ram"], "disk": None}

        expected_result = False, {"error": "ram_type_does_not_fit_what_you_have_on_your_mainboard"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    @patch(
        "resources.game_content.hardware",
        {
            "cpu": {"cpu": {"sockel": "foo"}},
            "mainboards": {
                "motherboard": {
                    "sockel": "foo",
                    "ram": {"ramSlots": 2, "typ": "xyz"},
                    "diskStorage": {"interface": "disk-interface"},
                }
            },
            "ram": {"ram": {"ramTyp": "xyz"}},
            "disk": {"disk": {"interface": "wrong-interface"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__disk_does_not_fit(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": ["ram"], "disk": ["disk"]}

        expected_result = False, {"error": "your_hard_drive_interface_does_not_fit_with_the_motherboards_one"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    @patch(
        "resources.game_content.hardware",
        {
            "cpu": {"cpu": {"sockel": "foo"}},
            "mainboards": {
                "motherboard": {
                    "sockel": "foo",
                    "ram": {"ramSlots": 2, "typ": "xyz"},
                    "diskStorage": {"interface": "disk-interface"},
                }
            },
            "ram": {"ram": {"ramTyp": "xyz"}},
            "disk": {"disk": {"interface": "disk-interface"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__no_ram(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": [], "disk": ["disk"]}

        expected_result = False, {"error": "you_need_at_least_one_ramstick"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    @patch(
        "resources.game_content.hardware",
        {
            "cpu": {"cpu": {"sockel": "foo"}},
            "mainboards": {
                "motherboard": {
                    "sockel": "foo",
                    "ram": {"ramSlots": 2, "typ": "xyz"},
                    "diskStorage": {"interface": "disk-interface"},
                }
            },
            "ram": {"ram": {"ramTyp": "xyz"}},
            "disk": {"disk": {"interface": "disk-interface"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__no_disk(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": ["ram"], "disk": []}

        expected_result = False, {"error": "you_need_at_least_one_harddrive"}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    @patch(
        "resources.game_content.hardware",
        {
            "cpu": {"cpu": {"sockel": "foo"}},
            "mainboards": {
                "motherboard": {
                    "sockel": "foo",
                    "ram": {"ramSlots": 2, "typ": "xyz"},
                    "diskStorage": {"interface": "disk-interface"},
                }
            },
            "ram": {"ram": {"ramTyp": "xyz"}},
            "disk": {"disk": {"interface": "disk-interface"}},
        },
    )
    @patch("resources.game_content.check_element_existence")
    def test__check_compatible__successful(self, cee_patch):
        cee_patch.return_value = True, {}
        elements = {"cpu": "cpu", "motherboard": "motherboard", "ram": ["ram"], "disk": ["disk"]}

        expected_result = True, {}
        actual_result = game_content.check_compatible(elements)

        self.assertEqual(expected_result, actual_result)

    def test__calculate_power(self):
        elements = {
            "cpu": list(hardware["cpu"])[0],
            "motherboard": list(hardware["mainboards"])[0],
            "ram": [list(hardware["ram"])[0]],
            "gpu": list(hardware["gpu"])[0],
            "disk": [list(hardware["disk"])[0]],
        }
        cpu = hardware["cpu"][elements["cpu"]]
        motherboard = hardware["mainboards"][elements["motherboard"]]
        ram = hardware["ram"][elements["ram"][0]]
        gpu = hardware["gpu"][elements["gpu"]]
        disk = hardware["disk"][elements["disk"][0]]

        expected_performance_cpu = cpu["cores"] * cpu["frequencyMax"]
        expected_performance_ram = (
            min(resolve_ram_type[motherboard["ram"]["typ"]], resolve_ram_type[ram["ramTyp"]]) * ram["ramSize"]
        )
        expected_performance_gpu = resolve_gpu_type[gpu["interface"]] * math.sqrt(gpu["ramSize"] * gpu["frequency"])
        expected_performance_disk = disk["capacity"] * math.log1p(disk["writingSpeed"] * disk["readingSpeed"])
        expected_performance_network = motherboard["networkCard"]["speed"]
        actual_result = game_content.calculate_power(elements)

        self.assertEqual(expected_performance_cpu, actual_result[0])
        self.assertEqual(expected_performance_ram, actual_result[1])
        self.assertEqual(expected_performance_gpu, actual_result[2])
        self.assertEqual(expected_performance_disk, actual_result[3])
        self.assertEqual(expected_performance_network, actual_result[4])

    @patch("resources.game_content.Hardware")
    def test__create_hardware(self, hardware_patch):
        elements = {
            "cpu": "cpu",
            "gpu": "gpu",
            "motherboard": "motherboard",
            "ram": ["ram1", "ram2"],
            "disk": ["disk1", "disk2"],
        }

        def create(device_uuid, element_name, element_type):
            self.assertEqual("my-device", device_uuid)

            if element_type in ("ram", "disk"):
                self.assertIn(element_name, elements[element_type])
                elements[element_type].remove(element_name)
                if not elements[element_type]:
                    del elements[element_type]
            else:
                if element_type == "mainboard":
                    element_type = "motherboard"
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
