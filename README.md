# Power

How much land would it take to replace U.S. petroleum with solar, wind, nuclear, hydro or geothermal, assuming we use just as much energy as we do today?

Power is a one-page, no-install web app for students. Pick how much energy to replace (petroleum, all fossil fuels, or all U.S. energy), check the power density of each source, and see the land needed as a share of the Lower 48 or all 50 states.

## Run it

Open `index.html` in any browser. No build step or internet connection is needed.

To publish it: on GitHub, go to **Settings → Pages**, choose **Deploy from a branch**, pick `main` and `/ (root)`, and save. The site appears at `https://dougalien.github.io/Power/`.

## How the numbers work

1. **Energy to replace.** EIA reports 2024 U.S. consumption in quadrillion Btu ("quads"). Petroleum was 35.3 quads. One quad per year averages about 33.4 GW, so petroleum is about 1.18 TW running all year.
2. **Power density.** Average watts actually delivered per square metre of land, capacity factor included. Defaults are medians from Lovering et al. (2022), converted with W/m² = 11,408 ÷ (ha/TWh/yr). Wind is shown two ways: the whole wind-farm area including spacing, and only the foundations and roads.
3. **Land needed** = power ÷ power density.

Every value is editable in the page and in `js/data.js`, which also lists all citations. A slider lets students credit electric drivetrains for wasting less energy than combustion engines; it defaults to replacing petroleum one-for-one.

The page also shows Layton (2008)'s energy-per-cubic-metre comparison, and a "work it out from a real plant" calculator so students can compute power density from a plant's capacity, area and capacity factor.

## Check the math

```
node test/calc.test.js
```

## Sources

- EIA (2025), U.S. primary energy consumption in 2024. https://www.eia.gov/todayinenergy/detail.php?id=65524
- Lovering et al. (2022), Land-use intensity of electricity production and tomorrow's energy landscape, PLOS ONE. https://doi.org/10.1371/journal.pone.0270155
- Miller & Keith (2018), Observation-based solar and wind power capacity factors and power densities, Environ. Res. Lett. https://doi.org/10.1088/1748-9326/aae102
- Denholm et al. (2009), Land-Use Requirements of Modern Wind Power Plants in the United States, NREL.
- Layton (2008), A comparison of energy densities of prevalent energy sources in units of joules per cubic meter, Int. J. Green Energy. https://doi.org/10.1080/15435070802498036
- U.S. Census Bureau, State Area Measurements (2010).
- Smil (2015), Power Density, MIT Press.
- LLNL U.S. energy flow charts.
