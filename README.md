# Power

How much land would it take to replace U.S. petroleum with solar, wind, nuclear, hydro or geothermal, assuming we use just as much energy as we do today?

Power is a Streamlit app for students, by Dougalien Systems. Pick how much energy to replace (petroleum, all fossil fuels, or all U.S. energy), check the power density of each source, and see the land needed as a share of the Lower 48 or all 50 states.

## Run it

Deploy on [Streamlit Community Cloud](https://share.streamlit.io): **Create app**, pick the `dougalien/Power` repo, branch `main`, main file `streamlit_app.py`.

To run it locally:

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## How the numbers work

1. **Energy to replace.** EIA reports 2024 U.S. consumption in quadrillion Btu ("quads"). Petroleum was 35.3 quads. One quad per year averages about 33.4 GW, so petroleum is about 1.18 TW running all year.
2. **Power density.** Average watts actually delivered per square meter of land, capacity factor included. Defaults are medians from Lovering et al. (2022), converted with W/m² = 11,408 ÷ (ha/TWh/yr). Wind is shown two ways: the whole wind-farm area including spacing, and only the foundations and roads.
3. **Land needed** = power ÷ power density.

Every value is editable in the app and in `power_core/data.py`, which also lists all citations. The arithmetic is in `power_core/calc.py`. A slider lets students credit electric drivetrains for wasting less energy than combustion engines; it defaults to replacing petroleum one-for-one.

The app also shows Layton (2008)'s energy-per-cubic-meter comparison, a "work it out from a real plant" calculator, and a units-trap walkthrough showing why dividing energy use by J/m³ gives a volume rather than an area, and how to convert J/m³ to W/m² of land.

## Check the math

```
python tests/test_calc.py
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
- MacKay (2009), Sustainable Energy – Without the Hot Air, UIT Cambridge. The land-area picture. https://www.withouthotair.com/
