"""Source data. Every number has a citation in REFERENCES."""
from dataclasses import dataclass

# U.S. primary energy consumption, 2024, quadrillion Btu. EIA, Today in Energy id 65524.
CONSUMPTION_2024 = {
    "petroleum": 35.3,
    "natural_gas": 34.2,
    "coal": 7.9,
    "nuclear": 8.2,
    "renewables": 8.6,
    "total": 94.2,
}

TARGETS = {
    "Petroleum only (35.3 quads)": CONSUMPTION_2024["petroleum"],
    "All fossil fuels: petroleum + gas + coal (77.4 quads)": round(
        CONSUMPTION_2024["petroleum"] + CONSUMPTION_2024["natural_gas"] + CONSUMPTION_2024["coal"], 1
    ),
    "All U.S. primary energy (94.2 quads)": CONSUMPTION_2024["total"],
    "Custom amount…": None,
}

SQMI_TO_KM2 = 2.589988
# Land areas. U.S. Census Bureau, State Area Measurements (2010).
LAND_KM2 = {
    "Lower 48 states": 2_959_064 * SQMI_TO_KM2,
    "All 50 states": 3_531_905 * SQMI_TO_KM2,
}
TEXAS_KM2 = 261_232 * SQMI_TO_KM2


def from_luie(ha_per_twh_yr: float) -> float:
    """Lovering et al. land-use intensity (ha/TWh/yr) -> W/m² (= 11,408 / LUIE)."""
    return 1e12 / 8766 / (ha_per_twh_yr * 1e4)


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    color: str
    clean: bool
    luie: float
    basis: str
    note: str

    @property
    def density(self) -> float:
        return from_luie(self.luie)


SOURCES = [
    Source("petroleum", "Petroleum (today's system)", "#8a5a2b", False, 410,
           "Proxy: natural-gas footprint (wells, pads, roads, pipelines)",
           "Lovering et al. had no oil data; their paper uses the natural-gas footprint as the stand-in for oil, "
           "and so does this app. Smil (2015) puts oil-field extraction alone at hundreds to thousands of W/m². "
           "Shown for comparison: it is what we are replacing."),
    Source("nuclear", "Nuclear", "#6b4fbb", True, 7.1,
           "Plant site, exclusion zone, and mining",
           "Median of 59 plants. U.S. capacity factor is about 90%."),
    Source("geothermal", "Geothermal", "#c2410c", True, 45,
           "Well pads, plant, pipelines",
           "Very dense, but only works where hot rock is near the surface, so it cannot be scaled at will."),
    Source("solar", "Solar PV (ground-mounted)", "#d4a017", True, 2000,
           "Fenced area of the solar farm (panels, rows, access roads)",
           "Median of 94 plants. U.S. utility PV capacity factor is roughly 24%. Rooftop solar uses no new land."),
    Source("csp", "Concentrated solar (CSP)", "#e07b00", True, 1300,
           "Mirror field and plant",
           "Needs strong direct sunlight, so in practice only the desert Southwest."),
    Source("wind_spacing", "Wind (total area incl. spacing)", "#1f77b4", True, 12000,
           "Whole wind-farm boundary: turbines spaced several rotor-diameters apart",
           "Most of this land stays usable for farming and ranching. Miller & Keith (2018) measured 0.50 W/m² "
           "for 411 U.S. wind farms; try that value too."),
    Source("wind_footprint", "Wind (foundations & roads only)", "#5fa8d3", True, 130,
           "Only land physically built on: foundations, pads, roads, substations",
           "Same wind farms as the row above, counting only the ground that is actually built on."),
    Source("hydro", "Hydroelectric (dams)", "#0f766e", True, 650,
           "Mostly the reservoir flooded behind the dam",
           "Huge spread between dams. Most good U.S. dam sites are already used."),
]
SOURCES_BY_ID = {s.id: s for s in SOURCES}

PRESETS = {
    "Lovering et al. 2022 medians (default)": {s.id: s.density for s in SOURCES},
    "Miller & Keith 2018 measured U.S. averages": {
        **{s.id: s.density for s in SOURCES}, "wind_spacing": 0.50, "solar": 5.4,
    },
}

# Layton (2008), Table 1 and text: energy per cubic meter (J/m³).
LAYTON_TABLE1 = [
    ("Solar radiation", 1.5e-6),
    ("Geothermal (heat pump)", 0.05),
    ("Tidal water (low)", 0.5),
    ("Wind at 10 mph (about 5 m/s)", 7),
    ("Tidal water (high)", 50),
    ("Human", 1000),
    ("Fat (food)", 3e7),
    ("Natural gas", 4e7),
    ("Automobile with fuel", 4e7),
    ("Gasoline", 1e10),
    ("Oil", 4.5e10),
    ("Purified uranium (Layton text)", 1.5e15),
]

REFERENCES = [
    ("U.S. Energy Information Administration (2025). U.S. primary energy production, consumption, and exports "
     "increased in 2024. Today in Energy.", "https://www.eia.gov/todayinenergy/detail.php?id=65524"),
    ("Lovering, J., Swain, M., Blomqvist, L., & Hernandez, R. R. (2022). Land-use intensity of electricity "
     "production and tomorrow's energy landscape. PLOS ONE 17(7): e0270155.",
     "https://doi.org/10.1371/journal.pone.0270155"),
    ("Miller, L. M., & Keith, D. W. (2018). Observation-based solar and wind power capacity factors and power "
     "densities. Environmental Research Letters 13(10): 104008.", "https://doi.org/10.1088/1748-9326/aae102"),
    ("Layton, B. E. (2008). A comparison of energy densities of prevalent energy sources in units of joules per "
     "cubic meter. International Journal of Green Energy 5: 438–455.", "https://doi.org/10.1080/15435070802498036"),
    ("Denholm, P., Hand, M., Jackson, M., & Ong, S. (2009). Land-Use Requirements of Modern Wind Power Plants in "
     "the United States. NREL/TP-6A2-45834.", "https://www.nrel.gov/docs/fy09osti/45834.pdf"),
    ("U.S. Census Bureau. State Area Measurements and Internal Point Coordinates (2010).",
     "https://www.census.gov/geographies/reference-files/2010/geo/state-area.html"),
    ("Smil, V. (2015). Power Density: A Key to Understanding Energy Sources and Uses. MIT Press.",
     "https://mitpress.mit.edu/9780262529457/power-density/"),
    ("Lawrence Livermore National Laboratory. Estimated U.S. Energy Consumption (annual energy flow charts).",
     "https://flowcharts.llnl.gov/"),
    ("MacKay, D. J. C. (2009). Sustainable Energy – Without the Hot Air. UIT Cambridge. ISBN 978-0-9544529-3-3. "
     "Picturing each energy source as the share of a country's land it would cover.",
     "https://www.withouthotair.com/"),
]
