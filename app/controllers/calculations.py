import math
from flask import Blueprint, request

calculation_controller = Blueprint('calculation_controller', __name__)


def xp_to_lvl_calc(xp):
    points = 0
    for level in range(1, 100):
        diff = int(level + 300 * math.pow(2, float(level) / 7))
        points += diff
        if points / 4 > xp:
            return level
    return 99


@calculation_controller.route("/calc/experience", methods=["POST"])
def experience_to_level():
    return str(xp_to_lvl_calc(request.json.get("xp")))


def string2bits(s=''):
    return [bin(ord(x))[2:].zfill(8) for x in s]


def bits2string(b=None):
    return ''.join([chr(int(x, 2)) for x in b])
