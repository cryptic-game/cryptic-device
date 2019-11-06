resolve_ram_type: dict = {"DDR1": 1, "DDR2": 2, "DDR3": 3, "DDR4": 4, "DDR5": 5}

resolve_gpu_type: dict = {"PCI": 1, "AGP": 2, "PCI_Express": 3}

hardware = {
    "start_pc": {
        "motherboard": "Zero MX One",
        "cpu": "CoreOne A100",
        "gpu": "Forcevid MX1000",
        "ram": ["Crossfire ZX100", "Crossfire ZX100"],
        "disk": ["HDD Elements Zero"],
    },
    "mainboards": {
        "Zero MX One": {
            "name": "Zero MX One",
            "case": "Mini-ATX",
            "cpuSockel": "XT2019",
            "numberCpu": 1,
            "coreTemperatureControl": False,
            "usbPorts": 1,
            "ram": {"ramSlots": 1, "maxRamSize": 1024, "typ": "DDR1", "frequency": [422, 922]},
            "graphicUnitOnBoard": False,
            "expansionSlots":
            {
                # Kann mit anderen Werten gefüllt und gemischt werden zb. PCI 2.0, 3.0, usw
                "PCI 1.0":
                {
                    "interface": "PCI",
                    "version": 1,
                    "interfaceSlots": 1,
                },
            },
            "diskStorage": {"diskSlots": 2, "interface": "IDE"},
            "networkPort": {"name": "LAN Megabit Ethernet", "interface": "RJ45", "speed": 1000},
            "power": 10,
        },
	"Zero MX Pro": {
            "name": "Zero MX Pro",
            "case": "Mini-ATX",
            "cpuSockel": "XT2019",
            "numberCpu": 1,
            "coreTemperatureControl": False,
            "usbPorts": 1,
            "ram": {"ramSlots": 1, "maxRamSize": 1024, "typ": "DDR1", "frequency": [922, 1122]},
            "graphicUnitOnBoard": False,
            "expansionSlots":
            {
                # Kann mit anderen Werten gefüllt und gemischt werden zb. PCI 2.0, 3.0, usw
                "PCI 2.0":
                {
                    "interface": "PCI",
                    "version": 2,
                    "interfaceSlots": 1,
                },
                "M.2":
                {
                    "interface": "M.2",
                    "version": None,
                    "interfaceSlots": 1,
                },
            },
            "diskStorage": {"diskSlots": 2, "interface": "IDE"},
            "networkPort": {"name": "LAN Megabit Ethernet", "interface": "RJ45", "speed": 1000},
            "power": 15,
        },
	"Zetta Ultimate M150": {
            "name": "Zetta Ultimate M150",
            "case": "Mini-ATX",
            "cpuSockel": "XT2019",
            "numberCpu": 1,
            "coreTemperatureControl": False,
            "usbPorts": 2,
            "ram": {"ramSlots": 2, "maxRamSize": 2048, "typ": "DDR2", "frequency": [922, 1222, 1422]},
            "graphicUnitOnBoard": False,
            "expansionSlots":
            {
                # Kann mit anderen Werten gefüllt und gemischt werden zb. PCI 2.0, 3.0, usw
                "PCI 1.0":
                {
                    "interface": "PCI",
                    "version": 1,
                    "interfaceSlots": 1,
                },
                "M.2":
                {
                    "interface": "M.2",
                    "version": None,
                    "interfaceSlots": 1,
                },
            },
            "diskStorage": {"diskSlots": 2, "interface": "IDE"},
            "networkPort": {"name": "LAN Gigabit Ethernet", "interface": "RJ45", "speed": 1000},
            "power": 20,
        },
    },
    "cpu": {
        "CoreOne A100": {
            "name": "CoreOne A100",
            "frequencyMin": 800,
            "frequencyMax": 800,
            "sockel": "XT2019",
            "cores": 1,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "power": 220,
            "graphicUnitExist": True,
            "graphicUnit": {"name": "HD Graphic 110", "ramSize": 512, "frequency": 350},
        },
        "CoreOne A110": {
            "name": "CoreOne A200",
            "frequencyMin": 1200,
            "frequencyMax": 1200,
            "sockel": "XT2019",
            "cores": 1,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "power": 240,
            "graphicUnitExist": True,
            "graphicUnit": {"name": "HD Graphic 110", "ramSize": 1024, "frequency": 350},
        },
	"QuadCore TX": {
            "name": "QuadCore TX",
            "frequencyMin": 2200,
            "frequencyMax": 2200,
            "sockel": "XT2021",
            "cores": 4,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 92,
            "power": 110,
            "graphicUnitExist": True,
            "graphicUnit": {"name": "HD Graphic 110", "ramSize": 1024, "frequency": 350},
        },
    },
    "processorCooler": [{"name": "CPU Cooler Mini", "coolerSpeed": 1, "sockel": "XT2019", "power": 10}],
    "ram": {
        "Crossfire ZX100": {"name": "Crossfire ZX100", "ramSize": 512, "ramTyp": "DDR1", "frequency": 422, "power": 5},
        "Crossfire ZX110": {
            "name": "Crossfire ZX110",
            "ramSize": 1024,
            "ramTyp": "DDR1",
            "frequency": 422,
            "power": 10,
        },
	"Crossfire ZX200": {
            "name": "Crossfire ZX200",
            "ramSize": 1024,
            "ramTyp": "DDR2",
            "frequency": 922,
            "power": 10,
        },
    },
    "gpu": {
        "Forcevid MX1000": {
            "name": "Forcevid MX1000",
            "ramSize": 128,
            "ramTyp": "DDR1",
            "frequency": 422,
            "interface": "AGP 1.0",
            "power": 120,
        },
        "Zetta TX2066": {
            "name": "Zetta TX2066",
            "ramSize": 2048,
            "ramTyp": "DDR1",
            "frequency": 1600,
            "interface": "PCI 1.0",
            "power": 400,
        },
    },
    "disk": {
        "HDD Elements Zero": {
            "name": "HDD Elements Zero",
            "diskTyp": "HDD",
            "capacity": 2000,
            "writingSpeed": 10,
            "readingSpeed": 20,
            "interface": "IDE",
            "power": 15,
        },
        "HDD Elements Two": {
            "name": "HDD Elements Two",
            "diskTyp": "HDD",
            "capacity": 5000,
            "writingSpeed": 60,
            "readingSpeed": 80,
            "interface": "SATA1",
            "power": 10,
        },
        "SSD 20GB MX": {
            "name": "SSD 20GB MX",
            "diskTyp": "SSD",
            "capacity": 20000,
            "writingSpeed": 150,
            "readingSpeed": 200,
            "interface": "SATA3",
            "power": 6,
        },
        "SSD 100GB M.2": {
            "name": "SSD 100GB M.2",
            "diskTyp": "M.2",
            "capacity": 100000,
            "writingSpeed": 1500,
            "readingSpeed": 1800,
            "interface": "SATA4",
            "power": 5,
        },
    },
    "powerPack": [
        {"name": "Crossfire XSOne 250 Watt", "totalPower": 250},
        {"name": "Name of Power Pack", "totalPower": 300},
    ],
    "case": [{"name": "Mini-ITX"}, {"name": "Mini-ATX"}, {"name": "ATX"}],
}
