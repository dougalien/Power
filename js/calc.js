/*
 * Power — the arithmetic. Kept separate so it can be checked by hand or by tests.
 */
(function (root) {
  "use strict";

  var J_PER_BTU = 1055.056; // International Table Btu
  var SECONDS_PER_YEAR = 365.25 * 24 * 3600; // 31,557,600 s
  var M2_PER_KM2 = 1e6;
  var KM2_PER_SQMI = 2.589988;

  // Quadrillion Btu per year -> average watts.
  function quadsToWatts(quads) {
    return (quads * 1e15 * J_PER_BTU) / SECONDS_PER_YEAR;
  }

  /*
   * Land needed (km²) for a source to deliver `quads` per year.
   * endUseFactor: units of new energy needed per unit of energy replaced
   *   (1 = replace one-for-one, "no decrease in energy use"; lower = credit for
   *   electric motors wasting less than combustion engines).
   * densityWm2: average output per m² of land.
   */
  function areaKm2(quads, densityWm2, endUseFactor) {
    if (!(densityWm2 > 0)) return Infinity;
    var f = endUseFactor == null ? 1 : endUseFactor;
    return (quadsToWatts(quads) * f) / densityWm2 / M2_PER_KM2;
  }

  // Area for a mix: shares is {id: fraction}, densities is {id: W/m²}.
  function mixAreaKm2(quads, shares, densities, endUseFactor) {
    var total = 0;
    Object.keys(shares).forEach(function (id) {
      if (shares[id] > 0) total += areaKm2(quads * shares[id], densities[id], endUseFactor);
    });
    return total;
  }

  // Derive W/m² from nameplate capacity, land area and capacity factor.
  function densityFromPlant(capacityMW, areaHa, capacityFactor) {
    if (!(areaHa > 0)) return 0;
    return (capacityMW * 1e6 * capacityFactor) / (areaHa * 1e4);
  }

  var CALC = {
    J_PER_BTU: J_PER_BTU,
    SECONDS_PER_YEAR: SECONDS_PER_YEAR,
    KM2_PER_SQMI: KM2_PER_SQMI,
    quadsToWatts: quadsToWatts,
    areaKm2: areaKm2,
    mixAreaKm2: mixAreaKm2,
    densityFromPlant: densityFromPlant
  };

  if (typeof module !== "undefined" && module.exports) module.exports = CALC;
  else root.POWER_CALC = CALC;
})(this);
