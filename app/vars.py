hardware = {
    "mainboards": [
        {
            "name": "Zero MX One",
            "case": "Mini-ITX",
            "sockel": "XT2019",
            "coreTemperatureControl": False,
            "usbPorts": 1,
            "power": 10,
            "ram": {
                "ramSlots": 1,
                "ramSize": 1000,
                "typ": "DDR1",
                "frequency": [422, 922, 1122],
            },
            "graphicUnit": {"onBoard": True, "interfaceSlots": None, "interface": None},
            "diskStorage": {"hdSlots": 1, "typ": "HDD", "interface": "IDE"},
            "networkCard": {
                "name": "Name der karte",
                "interface": "Gigabit Ethernet",
                "speed": 1000,
            },
        }
    ],
    "processor": [
        {
            "name": "CoreOne A100",
            "frequencyMin": 800,
            "frequencyMax": 800,
            "sockel": "XT2019",
            "cores": 1,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "power": 100,
            "graphicUnitExist": True,
            "graphicUnit": {"name": "HD Graphic 110", "ramSize": 512, "frequency": 622},
        },
        {
            "name": "CoreOne A200",
            "frequencyMin": 1200,
            "frequencyMax": 1200,
            "sockel": "XT2019",
            "cores": 1,
            "turboSpeed": False,
            "overClock": False,
            "maxTemperature": 72,
            "power": 110,
            "graphicUnitExist": True,
            "graphicUnit": {
                "name": "HD Graphic 110",
                "ramSize": 1000,
                "frequency": 622,
            },
        },
    ],
    "processorCooler": [
        {"name": "CPU Cooler Mini", "coolerSpeed": 1, "sockel": "XT2019", "power": 10}
    ],
    "ram": {
        "DDR1": [
            {
                "name": "Crossfire ZX100",
                "ramSize": 512,
                "ramTyp": "DDR1",
                "frequency": 422,
                "power": 5,
            },
            {
                "name": "Crossfire ZX100",
                "ramSize": 1000,
                "ramTyp": "DDR1",
                "frequency": 422,
                "power": 5,
            },
        ],
        "DDR2": [],
        "DDR3": [],
        "DDR4": [],
        "DDR5": [],
    },
    "graphiccards": {
        "agp": [
            {
                "name": "Forcevid MX1000",
                "ramSize": 128,
                "ramTyp": "DDR1",
                "frequency": 422,
                "interface": "AGP",
                "power": 120,
            }
        ],
        "pci": [
            {
                "name": "Zetta TX2066",
                "ramSize": 2000,
                "ramTyp": "DDR1",
                "frequency": 1600,
                "interface": "PCI",
                "power": 400,
            }
        ],
    },
    "diskStorage": {
        "HDD": [
            {
                "name": "HDD Elements Zero",
                "diskTyp": "HDD",
                "capacity": 2000,
                "writingSpeed": 10,
                "readingSpeed": 20,
                "interface": "IDE",
                "power": 7,
            },
            {
                "name": "HDD Elements Zero",
                "diskTyp": "HDD",
                "capacity": 5000,
                "writingSpeed": 10,
                "readingSpeed": 20,
                "interface": "IDE",
                "power": 7,
            },
        ],
        "SSD": [
            {
                "name": "Name der Festplatte",
                "diskTyp": "SSD",
                "capacity": 20000,
                "writingSpeed": 150,
                "readingSpeed": 200,
                "interface": "SATA3",
                "power": 6,
            }
        ],
        "M.2": [
            {
                "name": "Name der Festplatte",
                "diskTyp": "M.2",
                "capacity": 50000,
                "writingSpeed": 1500,
                "readingSpeed": 1800,
                "interface": "SATA4",
                "power": 5,
            }
        ],
    },
    "powerPack": [
        {"name": "Crossfire XSOne 250 Watt", "totalPower": 250},
        {"name": "Name of Power Pack", "totalPower": 300},
    ],
    "case": [{"name": "Mini-ITX"}, {"name": "Mini-ATX"}, {"name": "ATX"}],
}
