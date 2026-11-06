/*
 * Power — source data.
 * Every number here has a citation in SOURCES below. Change a value here (or in the
 * app's editable table) and every result updates.
 */
(function (root) {
  "use strict";

  // U.S. primary energy consumption, 2024, quadrillion Btu ("quads").
  // EIA, "U.S. primary energy production, consumption, and exports increased in 2024"
  // (Today in Energy, id 65524).
  var CONSUMPTION_2024 = {
    petroleum: 35.3,
    naturalGas: 34.2,
    coal: 7.9,
    nuclear: 8.2,
    renewables: 8.6,
    total: 94.2
  };

  // Targets the student can pick: how much energy must the clean source supply?
  var TARGETS = [
    { id: "petroleum", label: "Petroleum only (35.3 quads)", quads: CONSUMPTION_2024.petroleum },
    {
      id: "fossil",
      label: "All fossil fuels: petroleum + gas + coal (77.4 quads)",
      quads: CONSUMPTION_2024.petroleum + CONSUMPTION_2024.naturalGas + CONSUMPTION_2024.coal
    },
    { id: "total", label: "All U.S. primary energy (94.2 quads)", quads: CONSUMPTION_2024.total },
    { id: "custom", label: "Custom amount…", quads: null }
  ];

  // Land areas, km². U.S. Census Bureau, State Area Measurements (2010).
  var SQMI_TO_KM2 = 2.589988;
  var LAND = {
    contiguous: { label: "Lower 48 states (land)", km2: 2959064 * SQMI_TO_KM2 },
    all50: { label: "All 50 states (land)", km2: 3531905 * SQMI_TO_KM2 },
    texas: { label: "Texas (land)", km2: 261232 * SQMI_TO_KM2 }
  };

  /*
   * Power densities in watts of AVERAGE output per square metre of land (W/m²).
   * "Average" means capacity factor is already built in: this is the energy a plant
   * actually delivers over a year divided by 8,766 hours, divided by its land area.
   *
   * Lovering et al. (2022) report land-use intensity (LUIE) in hectares per TWh per year.
   * Conversion: W/m² = (1e12 Wh / 8766 h) / (LUIE × 10,000 m²) = 11,408 / LUIE.
   */
  function fromLUIE(haPerTWhYr) {
    return 1e12 / 8766 / (haPerTWhYr * 1e4);
  }

  var SOURCES_LIST = [
    {
      id: "petroleum",
      name: "Petroleum (today's system)",
      color: "#8a5a2b",
      clean: false,
      density: fromLUIE(410),
      luie: 410,
      basis: "Proxy: natural-gas footprint (wells, pads, roads, pipelines)",
      ref: "lovering",
      note:
        "Lovering et al. had no oil data; their paper uses the natural-gas footprint as the stand-in for oil, and so does this app. Smil (2015) puts oil-field extraction alone at hundreds to thousands of W/m². Shown for comparison: it is what we are replacing."
    },
    {
      id: "nuclear",
      name: "Nuclear",
      color: "#6b4fbb",
      clean: true,
      density: fromLUIE(7.1),
      luie: 7.1,
      basis: "Plant site, exclusion zone, and mining",
      ref: "lovering",
      note: "Median of 59 plants. Capacity factor in the U.S. is about 90%."
    },
    {
      id: "geothermal",
      name: "Geothermal",
      color: "#c2410c",
      clean: true,
      density: fromLUIE(45),
      luie: 45,
      basis: "Well pads, plant, pipelines",
      ref: "lovering",
      note:
        "Very dense, but only works where hot rock is near the surface. Resource-limited: it cannot be scaled to the whole country at will."
    },
    {
      id: "solar",
      name: "Solar PV (ground-mounted)",
      color: "#d4a017",
      clean: true,
      density: fromLUIE(2000),
      luie: 2000,
      basis: "Fenced area of the solar farm (panels, rows, access roads)",
      ref: "lovering",
      note:
        "Median of 94 plants. U.S. utility PV capacity factor is roughly 24%. Rooftop solar uses no new land and is not counted here."
    },
    {
      id: "csp",
      name: "Concentrated solar (CSP)",
      color: "#e07b00",
      clean: true,
      density: fromLUIE(1300),
      luie: 1300,
      basis: "Mirror field and plant",
      ref: "lovering",
      note: "Needs strong direct sunlight, so in practice only the desert Southwest."
    },
    {
      id: "windSpacing",
      name: "Wind (total area incl. spacing)",
      color: "#1f77b4",
      clean: true,
      density: fromLUIE(12000),
      luie: 12000,
      basis: "Whole wind-farm boundary: turbines must be spaced several rotor-diameters apart",
      ref: "lovering",
      note:
        "Most of this land stays usable (farms and ranches run between turbines), but nothing else that blocks wind can be built there. Miller & Keith (2018) measured 0.50 W/m² for 411 U.S. wind farms; try that value too."
    },
    {
      id: "windFootprint",
      name: "Wind (foundations & roads only)",
      color: "#5fa8d3",
      clean: true,
      density: fromLUIE(130),
      luie: 130,
      basis: "Only the land physically covered: turbine foundations, pads, roads, substations",
      ref: "lovering",
      note: "Same wind farms as the row above, counting only the ground that is actually built on."
    },
    {
      id: "hydro",
      name: "Hydroelectric (dams)",
      color: "#0f766e",
      clean: true,
      density: fromLUIE(650),
      luie: 650,
      basis: "Mostly the reservoir flooded behind the dam",
      ref: "lovering",
      note:
        "Huge spread between dams (the IQR is 2,300 ha/TWh/yr). Resource-limited: most good U.S. dam sites are already used."
    }
  ];

  // Alternative published values a student can switch to.
  var PRESETS = {
    lovering: {
      label: "Lovering et al. 2022 medians (default)",
      values: {}
    },
    millerKeith: {
      label: "Miller & Keith 2018 measured U.S. averages",
      values: { windSpacing: 0.5, solar: 5.4 }
    }
  };
  SOURCES_LIST.forEach(function (s) {
    PRESETS.lovering.values[s.id] = s.density;
  });

  // Layton (2008), Table 1: energy per cubic metre (J/m³). Student's source paper.
  var LAYTON_TABLE1 = [
    { name: "Solar radiation", jPerM3: 0.0000015 },
    { name: "Geothermal (heat pump)", jPerM3: 0.05 },
    { name: "Wind at 10 mph (5 m/s)", jPerM3: 7 },
    { name: "Tidal water (low)", jPerM3: 0.5 },
    { name: "Tidal water (high)", jPerM3: 50 },
    { name: "Human", jPerM3: 1000 },
    { name: "Fat (food)", jPerM3: 3e7 },
    { name: "Natural gas", jPerM3: 4e7 },
    { name: "Automobile with fuel", jPerM3: 4e7 },
    { name: "Gasoline", jPerM3: 1e10 },
    { name: "Oil", jPerM3: 4.5e10 },
    { name: "Purified uranium (Layton text)", jPerM3: 1.5e15 }
  ];

  var SOURCES = {
    eia: {
      short: "EIA 2024",
      text:
        "U.S. Energy Information Administration (2025). U.S. primary energy production, consumption, and exports increased in 2024. Today in Energy.",
      url: "https://www.eia.gov/todayinenergy/detail.php?id=65524"
    },
    lovering: {
      short: "Lovering et al. 2022",
      text:
        "Lovering, J., Swain, M., Blomqvist, L., & Hernandez, R. R. (2022). Land-use intensity of electricity production and tomorrow's energy landscape. PLOS ONE 17(7): e0270155.",
      url: "https://doi.org/10.1371/journal.pone.0270155"
    },
    millerKeith: {
      short: "Miller & Keith 2018",
      text:
        "Miller, L. M., & Keith, D. W. (2018). Observation-based solar and wind power capacity factors and power densities. Environmental Research Letters 13(10): 104008.",
      url: "https://doi.org/10.1088/1748-9326/aae102"
    },
    layton: {
      short: "Layton 2008",
      text:
        "Layton, B. E. (2008). A comparison of energy densities of prevalent energy sources in units of joules per cubic meter. International Journal of Green Energy 5: 438–455.",
      url: "https://doi.org/10.1080/15435070802498036"
    },
    census: {
      short: "U.S. Census",
      text: "U.S. Census Bureau. State Area Measurements and Internal Point Coordinates (2010).",
      url: "https://www.census.gov/geographies/reference-files/2010/geo/state-area.html"
    },
    smil: {
      short: "Smil 2015",
      text: "Smil, V. (2015). Power Density: A Key to Understanding Energy Sources and Uses. MIT Press.",
      url: "https://mitpress.mit.edu/9780262529457/power-density/"
    },
    denholm: {
      short: "Denholm et al. 2009",
      text:
        "Denholm, P., Hand, M., Jackson, M., & Ong, S. (2009). Land-Use Requirements of Modern Wind Power Plants in the United States. NREL/TP-6A2-45834.",
      url: "https://www.nrel.gov/docs/fy09osti/45834.pdf"
    },
    llnl: {
      short: "LLNL flow chart",
      text:
        "Lawrence Livermore National Laboratory. Estimated U.S. Energy Consumption (annual energy flow charts). Transportation is estimated at about 21% efficient.",
      url: "https://flowcharts.llnl.gov/"
    }
  };

  var DATA = {
    CONSUMPTION_2024: CONSUMPTION_2024,
    TARGETS: TARGETS,
    LAND: LAND,
    SOURCES_LIST: SOURCES_LIST,
    PRESETS: PRESETS,
    LAYTON_TABLE1: LAYTON_TABLE1,
    SOURCES: SOURCES,
    fromLUIE: fromLUIE
  };

  if (typeof module !== "undefined" && module.exports) module.exports = DATA;
  else root.POWER_DATA = DATA;
})(this);
