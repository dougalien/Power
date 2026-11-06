// Run with: node test/calc.test.js
const assert = require("assert");
const C = require("../js/calc.js");
const D = require("../js/data.js");

// 1 quad/yr ≈ 33.4 GW average
assert(Math.abs(C.quadsToWatts(1) / 1e9 - 33.43) < 0.05, "quad -> W");
// LUIE conversion: 7.1 ha/TWh/yr ≈ 1607 W/m²
assert(Math.abs(D.fromLUIE(7.1) - 1606.8) < 1, "LUIE conversion");
// 1 W/m² delivering 1 GW needs 1,000 km²
assert(Math.abs(C.areaKm2(1e9 / C.quadsToWatts(1), 1, 1) - 1000) < 1e-6, "area");
// end-use factor scales linearly
assert(Math.abs(C.areaKm2(10, 5, 0.5) * 2 - C.areaKm2(10, 5, 1)) < 1e-6, "end-use factor");
// mix of 100% one source equals that source
assert(Math.abs(C.mixAreaKm2(35.3, { solar: 1 }, { solar: 5.7 }, 1) - C.areaKm2(35.3, 5.7, 1)) < 1e-6, "mix");
// 100 MW on 3,400 ha at 35% ≈ 1.03 W/m²
assert(Math.abs(C.densityFromPlant(100, 3400, 0.35) - 1.029) < 0.01, "derive");

// Print the headline numbers for petroleum, lower 48
const land = D.LAND.contiguous.km2;
for (const s of D.SOURCES_LIST) {
  const a = C.areaKm2(D.CONSUMPTION_2024.petroleum, s.density, 1);
  console.log(s.name.padEnd(36), s.density.toFixed(2).padStart(8), "W/m²", Math.round(a).toLocaleString().padStart(12), "km²", (a / land * 100).toFixed(2).padStart(7) + "%");
}
console.log("All tests passed.");
