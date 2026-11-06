"""Power: how much land would it take to replace petroleum?

Run locally:  streamlit run streamlit_app.py
"""
import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from power_core import calc as C
from power_core import data as D

st.set_page_config(page_title="Power: How Much Land?", page_icon="⚡", layout="centered")

# ---------------------------------------------------------------- formatting
_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sig(n: float, digits: int = 3) -> float:
    if n == 0 or not math.isfinite(n):
        return n
    return round(n, digits - 1 - int(math.floor(math.log10(abs(n)))))


def fmt(n: float, digits: int = 3) -> str:
    if not math.isfinite(n):
        return "∞"
    v = sig(n, digits)
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    return f"{v:,.{max(0, digits - 1 - int(math.floor(math.log10(abs(v)))))}f}" if v else "0"


def sci(n: float) -> str:
    """9.9 × 10¹⁹ style for very large or small numbers."""
    if not math.isfinite(n):
        return "∞"
    e = int(math.floor(math.log10(abs(n))))
    if -2 <= e <= 5:
        return fmt(n)
    return f"{n / 10 ** e:.1f} × 10{str(e).translate(_SUP)}"


def pct(p: float) -> str:
    if not math.isfinite(p):
        return "∞"
    if p >= 10:
        return f"{p:.0f}%"
    if p >= 1:
        return f"{p:.1f}%"
    if p >= 0.01:
        return f"{p:.2f}%"
    return "<0.01%"


def power_str(w: float) -> str:
    if w >= 1e12:
        return f"{sig(w / 1e12)} TW"
    if w >= 1e9:
        return f"{sig(w / 1e9)} GW"
    return f"{sig(w / 1e6)} MW"


# ---------------------------------------------------------------- state
ss = st.session_state
ss.setdefault("densities", dict(D.PRESETS["Lovering et al. 2022 medians (default)"]))
ss.setdefault("editor_ver", 0)


def load_preset():
    ss.densities = dict(D.PRESETS[ss.preset])
    ss.editor_ver += 1


# ---------------------------------------------------------------- header
st.title("How much land would it take to replace petroleum?")
st.write(
    "Every power source needs land: wells and refineries, solar farms, wind farms, reactors, reservoirs. "
    "Pick how much energy to replace, check the assumptions, and see what share of the United States each "
    "source would cover. Every number is sourced and every number can be changed."
)

# ---------------------------------------------------------------- step 1
st.header("1. What are we replacing?")
target = st.selectbox("Energy to replace", list(D.TARGETS))
quads = D.TARGETS[target]
if quads is None:
    quads = st.number_input("Custom amount (quadrillion Btu per year)", min_value=0.0, value=35.3, step=0.1)
target_label = {
    0: "U.S. petroleum use", 1: "all U.S. fossil-fuel use", 2: "all U.S. energy use", 3: "the custom amount"
}[list(D.TARGETS).index(target)]

with st.expander("Replace it one-for-one, or credit electric efficiency?"):
    st.write(
        "The question assumes **no decrease in energy use**, so by default every joule of petroleum is replaced "
        "by one joule from the new source. That is the cautious, upper-end answer.\n\n"
        "Most petroleum is burned in engines, which turn most of it into waste heat. Lawrence Livermore estimates "
        "U.S. transportation is about 21% efficient, while an electric motor and battery are roughly 3–4 times "
        "better. So the same driving could need much less electricity than the petroleum it replaces."
    )
end_use = st.slider(
    "Units of new energy needed per unit replaced", 0.25, 1.0, 1.0, 0.05,
    help="1.00 = one-for-one (default). About 0.30 = full credit for electric drivetrains.",
)
watts = C.quads_to_watts(quads)
st.info(
    f"**{fmt(quads)} quadrillion Btu per year** is the same as running **{power_str(watts)}** of power around "
    "the clock, every hour of the year."
    + (f" With the efficiency credit, clean sources must supply {power_str(watts * end_use)}." if end_use < 1 else "")
)

# ---------------------------------------------------------------- step 2
st.header("2. How much power does each source make per square metre?")
st.write(
    "This is **power density**: the average watts a plant really delivers over a year (capacity factor "
    "included), divided by the land it uses. Higher means less land. Edit any value in the W/m² column."
)
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
c1.selectbox("Use published values from", list(D.PRESETS), key="preset", on_change=load_preset)
if c2.button("Reset", width="stretch"):
    ss.densities = dict(D.PRESETS["Lovering et al. 2022 medians (default)"])
    ss.editor_ver += 1
    st.rerun()

base = pd.DataFrame(
    {
        "Source": [s.name for s in D.SOURCES],
        "W/m²": [round(ss.densities[s.id], 3) for s in D.SOURCES],
        "What land is counted": [s.basis for s in D.SOURCES],
    },
    index=[s.id for s in D.SOURCES],
)
edited = st.data_editor(
    base,
    key=f"editor_{ss.editor_ver}",
    hide_index=True,
    width="stretch",
    disabled=["Source", "What land is counted"],
    column_config={"W/m²": st.column_config.NumberColumn(min_value=0.0, format="%.3g")},
)
densities = {sid: float(edited.loc[sid, "W/m²"] or 0) for sid in edited.index}
st.caption(
    "Defaults are medians from Lovering et al. (2022), a review of hundreds of real plants, converted from "
    "hectares per TWh per year (W/m² = 11,408 ÷ ha/TWh/yr)."
)
with st.expander("Notes on each source"):
    for s in D.SOURCES:
        st.markdown(f"**{s.name}.** {s.note} Lovering median: {s.luie:,g} ha/TWh/yr.")

# ---------------------------------------------------------------- step 3
st.header("3. Land needed")
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
land_name = c1.radio("Compare against", list(D.LAND_KM2), horizontal=True)
log_scale = c2.checkbox("Log scale")
land = D.LAND_KM2[land_name]

rows = []
for s in D.SOURCES:
    a = C.area_km2(quads, densities[s.id], end_use if s.clean else 1.0)
    rows.append({"s": s, "km2": a, "pct": a / land * 100})

clean = [r for r in rows if r["s"].clean and math.isfinite(r["km2"])]
if clean:
    lo = min(clean, key=lambda r: r["km2"])
    hi = max(clean, key=lambda r: r["km2"])
    st.success(
        f"To replace {target_label}, the land needed ranges from **{pct(lo['pct'])}** of the "
        f"{land_name.lower()} ({lo['s'].name.lower()}) to **{pct(hi['pct'])}** ({hi['s'].name.lower()})."
    )

fig = go.Figure(
    go.Bar(
        y=[r["s"].name for r in rows],
        x=[r["pct"] for r in rows],
        orientation="h",
        marker_color=[r["s"].color for r in rows],
        text=[f"{pct(r['pct'])} · {fmt(r['km2'])} km²" for r in rows],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{text}<extra></extra>",
    )
)
fig.add_vline(x=100, line_color="#b42318", line_width=2,
              annotation_text=f"All land in the {land_name.lower()}", annotation_position="top left")
fig.update_layout(
    height=60 + 44 * len(rows), margin=dict(l=10, r=40, t=40, b=30),
    xaxis_title="% of land", yaxis=dict(autorange="reversed"), showlegend=False,
)
if log_scale:
    fig.update_xaxes(type="log")
else:
    fig.update_xaxes(range=[0, max(105, max(r["pct"] for r in rows if math.isfinite(r["pct"])) * 1.25)])
st.plotly_chart(fig, width="stretch")

st.subheader("See it as area")
st.caption("The outlined square is the country's land area. Each coloured square has the area that source would need.")
items = sorted([r for r in rows if r["s"].id != "wind_footprint" and math.isfinite(r["km2"]) and r["km2"] > 0],
               key=lambda r: -r["km2"])
max_area = max([land] + [r["km2"] for r in items])
sq = go.Figure()


def side(a):
    return math.sqrt(a / max_area)


sq.add_shape(type="rect", x0=0, y0=0, x1=side(land), y1=side(land),
             line=dict(color="#b42318", width=2), fillcolor="rgba(128,128,128,0.12)")
sq.add_annotation(x=0.01, y=side(land) - 0.01, text=land_name, showarrow=False, xanchor="left", yanchor="top")
for r in items:
    sd = max(side(r["km2"]), 0.004)
    sq.add_shape(type="rect", x0=0, y0=0, x1=sd, y1=sd, line=dict(color="white", width=1),
                 fillcolor=r["s"].color, opacity=0.85)
    sq.add_trace(go.Scatter(x=[None], y=[None], mode="markers", marker=dict(color=r["s"].color, size=10, symbol="square"),
                            name=f"{r['s'].name} {pct(r['pct'])}"))
sq.update_xaxes(visible=False, range=[-0.01, 1.01])
sq.update_yaxes(visible=False, range=[-0.01, 1.01], scaleanchor="x")
sq.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0),
                 legend=dict(orientation="h", yanchor="top", y=-0.02))
st.plotly_chart(sq, width="stretch")

st.dataframe(
    pd.DataFrame(
        {
            "Source": [r["s"].name for r in rows],
            "km²": [fmt(r["km2"]) for r in rows],
            "square miles": [fmt(r["km2"] / C.KM2_PER_SQMI) for r in rows],
            "% of land": [pct(r["pct"]) for r in rows],
            "× Texas": [fmt(r["km2"] / D.TEXAS_KM2, 2) for r in rows],
        }
    ),
    hide_index=True,
    width="stretch",
)

# ---------------------------------------------------------------- step 4
st.header("4. Build a mix")
st.write("No country runs on one source. Set the share each clean source supplies. Shares are rescaled to add up to 100%.")
mix_ids = ["solar", "wind_spacing", "nuclear", "hydro", "geothermal", "csp"]
mix_defaults = {"solar": 50, "wind_spacing": 50}
weights = {}
cols = st.columns(2)
for i, sid in enumerate(mix_ids):
    name = "Wind" if sid == "wind_spacing" else D.SOURCES_BY_ID[sid].name
    weights[sid] = cols[i % 2].slider(name, 0, 100, mix_defaults.get(sid, 0), 5, key=f"mix_{sid}")
total_w = sum(weights.values())
if total_w == 0:
    st.warning("Move at least one slider.")
else:
    shares = {k: v / total_w for k, v in weights.items()}
    st.caption(" · ".join(f"{('Wind' if k == 'wind_spacing' else D.SOURCES_BY_ID[k].name)} {v:.0%}"
                          for k, v in shares.items() if v > 0))
    a = C.mix_area_km2(quads, shares, densities, end_use)
    st.success(
        f"This mix needs **{fmt(a)} km²** ({fmt(a / C.KM2_PER_SQMI)} sq mi), which is **{pct(a / land * 100)}** "
        f"of the {land_name.lower()}, or {fmt(a / D.TEXAS_KM2, 2)} times the size of Texas."
    )

# ---------------------------------------------------------------- step 5
st.header("5. Work it out from a real plant")
st.write(
    "Look up a real solar farm, wind farm or power plant: its nameplate capacity, its land area, and its capacity "
    "factor (the share of the year's maximum output it really produces)."
)
st.latex(r"\text{power density} = \frac{\text{capacity} \times \text{capacity factor}}{\text{land area}}")
c = st.columns(4)
mw = c[0].number_input("Capacity (MW)", min_value=0.0, value=100.0)
area_in = c[1].number_input("Land area", min_value=0.0, value=3400.0)
unit = c[2].selectbox("Unit", ["hectares", "acres", "km²", "square miles"])
cf = c[3].number_input("Capacity factor (%)", min_value=0.0, max_value=100.0, value=35.0)
area_ha = area_in * {"hectares": 1, "acres": 0.404686, "km²": 100, "square miles": 258.9988}[unit]
derived = C.density_from_plant(mw, area_ha, cf / 100)
st.info(f"≈ **{fmt(derived)} W/m²** of average output" if derived > 0 else "Enter a capacity, an area and a capacity factor.")
c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
clean_sources = [s for s in D.SOURCES if s.clean]
apply_to = c1.selectbox("Use this value for", [s.name for s in clean_sources],
                        index=[s.id for s in clean_sources].index("wind_spacing"))
if c2.button("Apply", width="stretch") and derived > 0:
    ss.densities = dict(densities)
    ss.densities[next(s.id for s in clean_sources if s.name == apply_to)] = derived
    ss.editor_ver += 1
    st.rerun()
st.caption("The example (100 MW on 3,400 ha at 35%) is a typical U.S. wind farm: NREL found about 34 ha of total "
           "project area per MW (Denholm et al. 2009).")

# ---------------------------------------------------------------- Layton
st.header("Energy per cubic metre (Layton 2008)")
st.write(
    "Layton compares sources by the energy held in one cubic metre of space. Fuels are a *store* of energy packed "
    "into a small volume; sunlight and wind are a *flow* that passes through. That is why oil is about 10¹⁶ times "
    "denser than sunlight by this measure, and why flows need large collecting areas instead."
)
lt = go.Figure(go.Bar(
    y=[n for n, _ in D.LAYTON_TABLE1], x=[v for _, v in D.LAYTON_TABLE1], orientation="h",
    marker_color="#1f6f5c", text=[f"{sci(v)} J/m³" for _, v in D.LAYTON_TABLE1], textposition="outside",
    cliponaxis=False, hovertemplate="%{y}: %{text}<extra></extra>",
))
lt.update_xaxes(type="log", title="J/m³ (log scale)", range=[-7, 17.5], dtick=3)
lt.update_layout(height=520, margin=dict(l=10, r=40, t=10, b=40), showlegend=False)
st.plotly_chart(lt, width="stretch")
st.caption("Values from Layton (2008), Table 1 and text. Layton also notes that covering an area about the size of "
           "Texas with 10%-efficient panels would match the whole world's 2008 energy use.")

# ---------------------------------------------------------------- units trap
st.header("The units trap: J/m³ is not W/m²")
w_trap = watts * end_use
j_trap = w_trap * C.SECONDS_PER_YEAR
land_m2 = land * 1e6
st.write(
    "It is tempting to take Layton's table and divide U.S. energy use by it. Watch what the units do. "
    f"This uses the amount from step 1: **{sci(j_trap)} J per year**, or **{sci(w_trap)} W**."
)


def vs_land(m2: float) -> str:
    r = m2 / land_m2
    return f"**{sci(r)} times** the {land_name.lower()}" if r >= 1 else f"**{pct(r * 100)}** of the {land_name.lower()}"


src = st.radio("Source", ["Wind", "Solar"], horizontal=True)
layton = 7.0 if src == "Wind" else 1.5e-6
w1, w2 = st.columns(2)
with w1.container(border=True):
    st.markdown("#### ✗ Energy per year ÷ J/m³")
    st.code(f"{sci(j_trap)} J ÷ {sci(layton)} J/m³", language=None)
    st.markdown("J ÷ (J/m³) = **m³**. That is a volume, not an area.")
    st.markdown(f"= {sci(j_trap / layton)}. Read as m², that would be {vs_land(j_trap / layton)}.")
with w2.container(border=True):
    st.markdown("#### ✗ Power ÷ J/m³")
    st.code(f"{sci(w_trap)} W ÷ {sci(layton)} J/m³", language=None)
    st.markdown("(J/s) ÷ (J/m³) = **m³/s**. That is a flow rate, not an area.")
    st.markdown(f"= {sci(w_trap / layton)}. Read as m², that would be {vs_land(w_trap / layton)}.")

with st.container(border=True):
    st.markdown("#### ✓ Turn J/m³ into W/m² first")
    st.markdown("Energy in a cubic metre only becomes power when it *moves*. Multiply by how fast it flows through a square metre:")
    st.latex(r"\frac{\text{J}}{\text{m}^3} \times \frac{\text{m}}{\text{s}} = \frac{\text{J}}{\text{m}^2\,\text{s}} = \frac{\text{W}}{\text{m}^2}")
    if src == "Wind":
        c = st.columns(3)
        v = c[0].number_input("Average wind speed (m/s)", 1.0, 20.0, 5.0, 0.5)
        sp1 = c[1].number_input("Spacing downwind (rotor diameters)", 1.0, 30.0, 10.0, 0.5)
        sp2 = c[2].number_input("Spacing crosswind (rotor diameters)", 1.0, 30.0, 5.0, 0.5)
        w = C.wind_chain(v, sp1, sp2)
        density_t = w["land_w_m2"]
        st.markdown(
            f"1. ½ × 1 kg/m³ × ({fmt(v)} m/s)² × 0.59 = **{fmt(w['energy_j_m3'])} J/m³**, the energy a turbine can take from each cubic metre of air\n"
            f"2. {fmt(w['energy_j_m3'])} J/m³ × {fmt(v)} m/s = **{fmt(w['rotor_w_m2'])} W/m²** per square metre of rotor the wind blows through\n"
            f"3. rotor area ÷ land per turbine = π/4 ÷ ({fmt(sp1)} × {fmt(sp2)}) = **{pct(w['rotor_share'] * 100)}**, because turbines must be spread out or they steal each other's wind\n"
            f"4. {fmt(w['rotor_w_m2'])} × {w['rotor_share']:.4f} = **{fmt(density_t, 2)} W/m² of land** (compare: 0.50 measured by Miller & Keith, 0.95 Lovering median)"
        )
    else:
        c = st.columns(3)
        sun = c[0].number_input("Average sunlight on the ground (W/m²)", 1.0, 400.0, 150.0)
        eff = c[1].number_input("Panel efficiency (%)", 1.0, 100.0, 20.0)
        gcr = c[2].number_input("Share of land covered by panels (%)", 1.0, 100.0, 40.0)
        s_ = C.solar_chain(sun, eff / 100, gcr / 100)
        density_t = s_["land_w_m2"]
        st.markdown(
            "1. 1,361 W/m² ÷ 3 × 10⁸ m/s = **4.5 × 10⁻⁶ J/m³**: sunlight above the atmosphere has the same tiny order as "
            "Layton's 1.5 × 10⁻⁶, but it moves at the speed of light\n"
            f"2. after night, clouds and sun angle: about **{fmt(sun)} W/m²** on the ground (Layton: 100–150 W/m² U.S. average)\n"
            f"3. {fmt(sun)} × {eff:g}% efficient = **{fmt(s_['panel_w_m2'])} W/m²** per square metre of panel\n"
            f"4. {fmt(s_['panel_w_m2'])} × {gcr:g}% of the ground covered = **{fmt(density_t, 2)} W/m² of land** "
            "(rows are spaced so they don't shade each other; compare 5.4 measured, 5.7 median)"
        )
    area_t = w_trap / density_t if density_t > 0 else math.inf
    st.success(f"{sci(w_trap)} W ÷ {fmt(density_t, 2)} W/m² = {sci(area_t)} m², which is {vs_land(area_t)}.")
st.caption(
    "Wind uses Layton's method: ½ × air density (1 kg/m³) × speed², times the Betz limit (59%). Real wind speeds vary, "
    "so a site's average of speed³ is higher than (average speed)³, while turbines also stop gaining above their rated "
    "speed. Treat this as an order-of-magnitude check, then compare it with the measured values in step 2."
)

# ---------------------------------------------------------------- caveats & sources
st.header("What this calculator leaves out")
st.markdown(
    "- **Storage and backup.** Solar and wind vary by hour and season. Batteries, pumped hydro or backup plants add cost and some land.\n"
    "- **Transmission lines** to move power from where it is made to where it is used.\n"
    "- **Mining and manufacturing** land for materials, except where the source study included it (nuclear figures include uranium mining).\n"
    "- **Resource limits.** Hydro and geothermal are dense but only work in certain places; most good U.S. dam sites are already built.\n"
    "- **Shared land.** Land inside a wind farm is mostly still farmed. Rooftop solar uses no new land at all.\n"
    "- **Turning electricity into fuel.** Planes, ships and some industry use petroleum in ways that are hard to electrify directly."
)
st.header("Sources")
st.markdown("\n".join(f"{i}. {text} [{url.split('//')[1]}]({url})" for i, (text, url) in enumerate(D.REFERENCES, 1)))
