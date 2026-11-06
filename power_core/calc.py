"""The arithmetic. Kept separate from the app so it can be checked by hand or by tests."""
import math

J_PER_BTU = 1055.056  # International Table Btu
SECONDS_PER_YEAR = 365.25 * 24 * 3600  # 31,557,600 s
KM2_PER_SQMI = 2.589988


def quads_to_watts(quads: float) -> float:
    """Quadrillion Btu per year -> average watts."""
    return quads * 1e15 * J_PER_BTU / SECONDS_PER_YEAR


def area_km2(quads: float, density_w_m2: float, end_use_factor: float = 1.0) -> float:
    """Land (km²) a source needs to deliver `quads` per year.

    end_use_factor: units of new energy needed per unit replaced (1 = one-for-one).
    density_w_m2: average output per m² of land, capacity factor included.
    """
    if not density_w_m2 or density_w_m2 <= 0:
        return math.inf
    return quads_to_watts(quads) * end_use_factor / density_w_m2 / 1e6


def mix_area_km2(quads: float, shares: dict, densities: dict, end_use_factor: float = 1.0) -> float:
    """Total land for a mix. shares: {id: fraction}, densities: {id: W/m²}."""
    return sum(
        area_km2(quads * f, densities[i], end_use_factor) for i, f in shares.items() if f > 0
    )


def density_from_plant(capacity_mw: float, area_ha: float, capacity_factor: float) -> float:
    """W/m² from nameplate capacity, land area and capacity factor (0–1)."""
    if not area_ha or area_ha <= 0:
        return 0.0
    return capacity_mw * 1e6 * capacity_factor / (area_ha * 1e4)


def wind_chain(speed_m_s: float, spacing_down: float, spacing_cross: float,
               air_density: float = 1.0, betz: float = 0.59) -> dict:
    """Layton's wind method, carried through to W per m² of land."""
    energy_j_m3 = 0.5 * air_density * speed_m_s ** 2 * betz
    rotor_w_m2 = energy_j_m3 * speed_m_s
    rotor_share = math.pi / (4 * spacing_down * spacing_cross)
    return {
        "energy_j_m3": energy_j_m3,
        "rotor_w_m2": rotor_w_m2,
        "rotor_share": rotor_share,
        "land_w_m2": rotor_w_m2 * rotor_share,
    }


def solar_chain(ground_w_m2: float, efficiency: float, ground_cover: float) -> dict:
    """Sunlight on the ground -> W per m² of land. efficiency and ground_cover are 0–1."""
    panel = ground_w_m2 * efficiency
    return {"panel_w_m2": panel, "land_w_m2": panel * ground_cover}
