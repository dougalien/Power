"""Run with: python -m pytest  (or python tests/test_calc.py)"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from power_core import calc as C  # noqa: E402
from power_core import data as D  # noqa: E402


def test_quad_to_watts():
    assert abs(C.quads_to_watts(1) / 1e9 - 33.43) < 0.05


def test_luie_conversion():
    assert abs(D.from_luie(7.1) - 1606.8) < 1


def test_area():
    q = 1e9 / C.quads_to_watts(1)  # quads giving 1 GW
    assert abs(C.area_km2(q, 1.0) - 1000) < 1e-6
    assert math.isinf(C.area_km2(1, 0))


def test_end_use_and_mix():
    assert abs(C.area_km2(10, 5, 0.5) * 2 - C.area_km2(10, 5, 1)) < 1e-6
    assert abs(C.mix_area_km2(35.3, {"solar": 1}, {"solar": 5.7}) - C.area_km2(35.3, 5.7)) < 1e-6


def test_derive_and_chains():
    assert abs(C.density_from_plant(100, 3400, 0.35) - 1.029) < 0.01
    w = C.wind_chain(5, 10, 5)
    assert abs(w["energy_j_m3"] - 7.375) < 1e-9  # Layton's ~7 J/m³
    assert abs(w["land_w_m2"] - 0.579) < 0.01
    assert abs(C.solar_chain(150, 0.2, 0.4)["land_w_m2"] - 12) < 1e-9


def test_headline_numbers():
    land = D.LAND_KM2["Lower 48 states"]
    pct = lambda sid: C.area_km2(D.CONSUMPTION_2024["petroleum"], D.SOURCES_BY_ID[sid].density) / land * 100
    assert abs(pct("solar") - 2.70) < 0.05
    assert abs(pct("wind_spacing") - 16.2) < 0.1
    assert pct("nuclear") < 0.01


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All tests passed.")
