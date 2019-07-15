import json
from vars import hardware


def check_compatible(elements: dict, new: str, hw_type: str) -> bool:

    if hw_type == "cpu":

        if "motherboard" in elements.keys():

            if hardware["cpu"][new]["sockel"] != hardware["cpu"][new]["sockel"]:
                return False

        else:
            return False

    return True


def calculate_power(
    elements: dict
) -> int:

    cpu: str = elements["cpu"]
    motherboard: str = elements["motherboard"]

    power: int = min(
        hardware["cpu"][cpu]["cycleRate"],
        hardware["motherboard"][motherboard]["cycleRate"],
    ) * hardware["cpu"][cpu]["freq"]

    if "gpu" in elements.keys():

        gpu: str = elements["gpu"]

        power += (
            min(
                hardware["gpu"][gpu]["cylerate"],
                hardware["motherboard"][motherboard]["cylerate"],
            )
            * hardware["cpu"][cpu]["freq"]
        )

    return power


def add_able(elements: dict, type_new: str) -> bool:

    if type_new == "cpu" and "cpu" in elements.keys():
        return False
    if type_new == "motherboard" and "motherboard" in elements.keys():
        return False
    if type_new == "gpu" and "gpu" in elements.keys():
        return False
    if type_new == "harddrive":
        # TODO check for multiple harddrives dependinng on spaces in the motherboard
        pass

    return True
