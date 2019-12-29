hardware = {
    # Start PC
    "start_pc": {
        "mainboards": "Zero MX One",
        "cpu": "CoreOne A100",
        "processorCooler": "CPU Cooler Mini",
        "gpu": None,
        "ram": ["Crossfire One"],
        "disk": ["HDD Elements Zero A"],
        "powerPack": "Crossfire XSOne 500 Watt",
        "case": "Mini-ITX"
    },
    # ----- Mainboards -----
    "mainboards": {
        # Start Mainboard
        "Zero MX One": {
            "name": "Zero MX One",
            "case": "Mini-ITX",
            "cpuSockel": "XT2019",
            "cpuSlots": 1,
            "coreTemperatureControl": False,
            "usbPorts": 0,
            "ram": {"ramSlots": 1, "maxRamSize": 128, "ramTyp": [("DDR", 1)], "frequency": [422]},
            "graphicUnitOnBoard": {"name": "nForce 1", "ramSize": 128, "frequency": 322},
            "expansionSlots": {
                # Kann mit anderen Werten gemischt werden zb. AGP 1.0, PCI 1.0, PCI 2.0, usw
                "AGP 1.0": {"interface": "AGP", "version": 1, "interfaceSlots": 1},
            },
            "diskStorage": {"diskSlots": 2, "interface": [("IDE", 1)]},
            "networkPort": {"name": "LAN Megabit Ethernet", "interface": "RJ45", "speed": 100},
            "power": 10
        },
        # Weitere Mainboards
        "Zero MX Pro": {
            "name": "Zero MX Pro",
            "case": "Mini-ATX",
            "cpuSockel": "XT2019",
            "cpuSlots": 1,
            "coreTemperatureControl": False,
            "usbPorts": 1,
            "ram": {"ramSlots": 1, "maxRamSize": 1024, "ramTyp": [("DDR", 1)], "frequency": [922, 1122]},
            "graphicUnitOnBoard": {"name": "nForce 1", "ramSize": 128, "frequency": 322},
            "expansionSlots": {
                # Kann mit anderen Werten gemischt werden zb. AGP 1.0, PCI 1.0, PCI 2.0, usw
                "AGP 1.0": {"interface": "AGP", "version": 1, "interfaceSlots": 1},
            },
            "diskStorage": {"diskSlots": 2, "interface": [("IDE", 1)]},
            "networkPort": {"name": "LAN Megabit Ethernet", "interface": "RJ45", "speed": 100},
            "power": 15
        },
        "Zetta Ultimate M150": {
            "name": "Zetta Ultimate M150",
            "case": "Mini-ATX",
            "cpuSockel": "XT2020",
            "cpuSlots": 1,
            "coreTemperatureControl": False,
            "usbPorts": 2,
            "ram": {"ramSlots": 2, "maxRamSize": 2048, "ramTyp": [("DDR", 1), ("DDR", 2)], "frequency": [922, 1222, 1422]},
            "graphicUnitOnBoard": None,
            "expansionSlots": {
                # Kann mit anderen Werten gemischt werden zb. AGP 1.0, PCI 1.0, PCI 2.0, usw
                "PCI 1.0": {"interface": "PCI", "version": 1, "interfaceSlots": 1},
            },
            "diskStorage": {"diskSlots": 2, "interface": [("SATA", 1)]},
            "networkPort": {"name": "LAN Gigabit Ethernet", "interface": "RJ45", "speed": 1000},
            "power": 20
        },
        "Zeus Professional X2": {
            "name": "Zeus Professional X2",
            "case": "ATX",
            "cpuSockel": "XT2021",
            "cpuSlots": 1,
            "coreTemperatureControl": False,
            "usbPorts": 2,
            "ram": {"ramSlots": 2, "maxRamSize": 4096, "ramTyp": [("DDR", 2), ("DDR", 3)], "frequency": [1422, 1622]},
            "graphicUnitOnBoard": None,
            "expansionSlots": {
                # Kann mit anderen Werten gemischt werden zb. AGP 1.0, PCI 1.0, PCI 2.0, usw
                "PCI 2.0": {"interface": "PCI", "version": 2, "interfaceSlots": 1},
            },
            "diskStorage": {"diskSlots": 3, "interface": [("SATA", 1), ("SATA", 3)]},
            "networkPort": {"name": "LAN Gigabit Ethernet", "interface": "RJ45", "speed": 1000},
            "power": 20
        },
        "Zeus Professional X3": {
            "name": "Zeus Professional X3",
            "case": "ATX",
            "cpuSockel": "XT2021",
            "cpuSlots": 1,
            "coreTemperatureControl": False,
            "usbPorts": 2,
            "ram": {"ramSlots": 2, "maxRamSize": 8192, "ramTyp": [("DDR", 3), ("DDR", 4)], "frequency": [1622, 1800, 2400]},
            "graphicUnitOnBoard": None,
            "expansionSlots": {
                # Kann mit anderen Werten gemischt werden zb. AGP 1.0, PCI 1.0, PCI 2.0, usw
                "PCI 2.0": {"interface": "PCI", "version": 2, "interfaceSlots": 1},
                "PCIe 3.0": {"interface": "PCIe", "version": 3, "interfaceSlots": 1},
            },
            "diskStorage": {"diskSlots": 3, "interface": [("SATA", 1), ("SATA", 3)]},
            "networkPort": {"name": "LAN Gigabit Ethernet", "interface": "RJ45", "speed": 1000},
            "power": 20
        },
    },
    # ----- Processor -----
    "cpu": {
        # Single Core
        "CoreOne A100": {  # Start CPU
            "name": "CoreOne A100",
            "frequencyMin": 500,
            "frequencyMax": 500,
            "sockel": "XT2019",
            "cores": 1,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "graphicUnitExist": None,
            "power": 220
        },
        "CoreOne A110": {
            "name": "CoreOne A110",
            "frequencyMin": 800,
            "frequencyMax": 800,
            "sockel": "XT2019",
            "cores": 1,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "graphicUnitExist": None,
            "power": 240
        },
        # Dual Core
        "DualCore M101": {
            "name": "DualCore M101",
            "frequencyMin": 800,
            "frequencyMax": 800,
            "sockel": "XT2020",
            "cores": 2,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "graphicUnitExist": {"name": "HD Graphic 100", "ramSize": 512, "frequency": 522},
            "power": 250
        },
        # Quad Core
        "QuadCore TX900": {
            "name": "QuadCore TX900",
            "frequencyMin": 2200,
            "frequencyMax": 2200,
            "sockel": "XT2021",
            "cores": 4,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 92,
            "graphicUnitExist": {"name": "HD Graphic 110", "ramSize": 1024, "frequency": 522},
            "power": 210
        },
        "QuadCore TX950": {
            "name": "QuadCore TX950",
            "frequencyMin": 3000,
            "frequencyMax": 3000,
            "sockel": "XT2021",
            "cores": 4,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 92,
            "graphicUnitExist": {"name": "HD Graphic 115", "ramSize": 1024, "frequency": 922},
            "power": 230
        },
    },
    # ----- ProzessorCooler -----
    "processorCooler": {
        "CPU Cooler Mini": {"name": "CPU Cooler Mini", "coolerSpeed": 1, "sockel": "XT2019", "power": 10},
        "CPU Cooler Plus": {"name": "CPU Cooler Plus", "coolerSpeed": 2, "sockel": "XT2020", "power": 10},
        "CPU Cooler Pro": {"name": "CPU Cooler Pro", "coolerSpeed": 4, "sockel": "XT2021", "power": 15},
    },
    # ----- RAM -----
    "ram": {
        # Start RAM
        "Crossfire One": {"name": "Crossfire One", "ramSize": 128, "ramTyp": {"interface": "DDR", "version": 1}, "frequency": 422, "power": 5},
        "Crossfire ZX100": {"name": "Crossfire ZX100", "ramSize": 512, "ramTyp": {"interface": "DDR", "version": 1}, "frequency": 922, "power": 5},
        "Crossfire ZX110": {
            "name": "Crossfire ZX110",
            "ramSize": 1024,
            "ramTyp": {"interface": "DDR", "version": 1},
            "frequency": 922,
            "power": 10
        },
        "Crossfire ZX120": {
            "name": "Crossfire ZX120",
            "ramSize": 1024,
            "ramTyp": {"interface": "DDR", "version": 1},
            "frequency": 1122,
            "power": 10
        },
        "Crossfire ZX200": {
            "name": "Crossfire ZX200",
            "ramSize": 1024,
            "ramTyp": {"interface": "DDR", "version": 2},
            "frequency": 1222,
            "power": 10
        },
        "Crossfire ZX210": {
            "name": "Crossfire ZX210",
            "ramSize": 1024,
            "ramTyp": {"interface": "DDR", "version": 2},
            "frequency": 1422,
            "power": 10
        },
        "Crossfire ZX220": {
            "name": "Crossfire ZX220",
            "ramSize": 2048,
            "ramTyp": {"interface": "DDR", "version": 3},
            "frequency": 1622,
            "power": 10
        },
        "Crossfire P50": {
            "name": "Crossfire P50",
            "ramSize": 4096,
            "ramTyp": {"interface": "DDR", "version": 4},
            "frequency": 1800,
            "power": 10
        },
        "Crossfire P60": {
            "name": "Crossfire P60",
            "ramSize": 4096,
            "ramTyp": {"interface": "DDR", "version": 4},
            "frequency": 2400,
            "power": 10
        },
    },
    # ----- Graphic cards -----
    "gpu": {
        # Start GPU
        "Forcevid MX1000": {
            "name": "Forcevid MX1000",
            "ramSize": 512,
            "ramTyp": {"interface": "GDDR", "version": 1},
            "frequency": 422,
            "interface": {"interface": "AGP", "version": 1},
            "power": 80
        },
        "Zetta TX2066": {
            "name": "Zetta TX2066",
            "ramSize": 1024,
            "ramTyp": {"interface": "GDDR", "version": 1},
            "frequency": 1200,
            "interface": {"interface": "PCI", "version": 1},
            "power": 220
        },
        "Zetta TX2066 Pro": {
            "name": "Zetta TX2066 Pro",
            "ramSize": 2048,
            "ramTyp": {"interface": "GDDR", "version": 2},
            "frequency": 1444,
            "interface": {"interface": "PCI", "version": 2},
            "power": 280
        },
    },
    # ----- Disks -----
    "disk": {
        # Start Disk
        "HDD Elements Zero A": {
            "name": "HDD Elements Zero A",
            "diskTyp": "HDD",
            "capacity": 2000,
            "writingSpeed": 8,
            "readingSpeed": 16,
            "interface": {"interface": "IDE", "version": 1},
            "power": 15
        },
        "HDD Elements Zero B": {
            "name": "HDD Elements Zero B",
            "diskTyp": "HDD",
            "capacity": 5000,
            "writingSpeed": 15,
            "readingSpeed": 25,
            "interface": {"interface": "IDE", "version": 1},
            "power": 15
        },
        "HDD Elements Two": {
            "name": "HDD Elements Two",
            "diskTyp": "HDD",
            "capacity": 10000,
            "writingSpeed": 60,
            "readingSpeed": 80,
            "interface": {"interface": "SATA", "version": 1},
            "power": 15
        },
        "SSD 20GB MX": {
            "name": "SSD 20GB MX",
            "diskTyp": "SSD",
            "capacity": 20000,
            "writingSpeed": 150,
            "readingSpeed": 200,
            "interface": {"interface": "SATA", "version": 3},
            "power": 6
        },
        "SSD 100GB M.2": {
            "name": "SSD 100GB M.2",
            "diskTyp": "SSD",
            "capacity": 100000,
            "writingSpeed": 1500,
            "readingSpeed": 1800,
            "interface": {"interface": "PCIe", "version": 3},
            "power": 5
        },
    },
    # ----- PowerPack -----
    "powerPack": [
        {"name": "Crossfire XSOne 500 Watt", "totalPower": 500},
        {"name": "Zeus X10 Pro", "totalPower": 700},
    ],
    # ----- Case -----
    "case": [{"name": "Mini-ITX"}, {"name": "Mini-ATX"}, {"name": "ATX"}],
}
