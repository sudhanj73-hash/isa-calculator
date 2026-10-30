"""
app.py - Standard Atmosphere (ISA) Calculator website, built with Streamlit.
Run with:  streamlit run app.py
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import isa

FT = 0.3048  # metres per foot

# ==================================================================
# EDIT THIS SECTION WITH YOUR OWN DETAILS (only place you need to change)
# ==================================================================
PROJECT_TITLE = "Standard Atmosphere (ISA) Calculator"
TEAM_MEMBERS = [
    "Sudhan J",              # <- replace with your full name
    "revathi I",
    "bhavadharini S",
    "KANISHKA B",
]
COLLEGE = "KPR INSTITUTE OF ENGINEERING AND TECHNNOLOGY"
DEPARTMENT = " Mechanical Engineering AND INFORMATION TECHNOLOGY"
YEAR = "2nd Year"
GUIDE = ""        # set to "" to hide this line
GITHUB_URL = "https://github.com/sudhanj73-hash/isa-calculator"
# ==================================================================

TEAM_TEXT = ", ".join(TEAM_MEMBERS)

st.set_page_config(page_title=f"{PROJECT_TITLE} | {TEAM_MEMBERS[0]}",
                   page_icon="✈️", layout="wide")

st.title(f"✈️ {PROJECT_TITLE}")
st.caption(
    "Pressure, temperature, density and speed of sound from 0 to 20 km, "
    "with density altitude and hot/cold day correction."
)
st.markdown(f"**Developed by:** {TEAM_TEXT}  \n{DEPARTMENT}, {COLLEGE}")

# ------------------------------------------------------------------
# Sidebar inputs
# ------------------------------------------------------------------
st.sidebar.header("Inputs")

alt_unit = st.sidebar.radio("Altitude unit", ["m", "ft", "km"], horizontal=True)
limits = {"m": (0.0, 20000.0, 1000.0, 100.0),
          "ft": (0.0, 65600.0, 5000.0, 500.0),
          "km": (0.0, 20.0, 1.0, 0.1)}
lo, hi, default, step = limits[alt_unit]
alt_input = st.sidebar.number_input(
    f"Pressure altitude ({alt_unit})", min_value=lo, max_value=hi,
    value=default, step=step)

delta_T = st.sidebar.slider(
    "Temperature deviation from standard (°C)", -40, 40, 0,
    help="0 = standard day. +15 means 15 °C hotter than ISA at that altitude.")

# convert the input altitude to metres for the calculations
to_m = {"m": 1.0, "ft": FT, "km": 1000.0}[alt_unit]
h = min(alt_input * to_m, 20000.0)

st.sidebar.header("Output units")
p_unit = st.sidebar.selectbox("Pressure", ["Pa", "kPa", "hPa (mbar)", "psi", "atm"])
t_unit = st.sidebar.selectbox("Temperature", ["°C", "K", "°F"])

st.sidebar.divider()
st.sidebar.markdown("**Project by**")
for member in TEAM_MEMBERS:
    st.sidebar.markdown(f"- {member}")
st.sidebar.markdown(f"[Source code on GitHub]({GITHUB_URL})")

# ------------------------------------------------------------------
# Calculation
# ------------------------------------------------------------------
res = isa.atmosphere(h, delta_T)
std = isa.atmosphere(h, 0.0)
h_density = isa.density_altitude(res["density"])


def fmt_pressure(p):
    factors = {"Pa": 1, "kPa": 1e-3, "hPa (mbar)": 1e-2, "psi": 1 / 6894.757, "atm": 1 / 101325}
    return p * factors[p_unit]


def fmt_temp(t_k):
    if t_unit == "K":
        return t_k
    if t_unit == "°C":
        return t_k - 273.15
    return (t_k - 273.15) * 9 / 5 + 32


# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------
st.subheader(f"Results at {h:,.0f} m  ({h / FT:,.0f} ft)")

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Temperature ({t_unit})", f"{fmt_temp(res['temperature_K']):.2f}")
c2.metric(f"Pressure ({p_unit})", f"{fmt_pressure(res['pressure_Pa']):.4g}")
c3.metric("Density (kg/m³)", f"{res['density']:.4f}")
c4.metric("Speed of sound (m/s)", f"{res['speed_of_sound']:.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Density altitude (ft)", f"{h_density / FT:,.0f}",
          delta=f"{(h_density - h) / FT:+,.0f} ft vs pressure alt", delta_color="inverse")
c6.metric("Density ratio σ", f"{res['density_ratio']:.4f}")
c7.metric("Dynamic viscosity (Pa·s)", f"{res['viscosity']:.3e}")
c8.metric("Kinematic viscosity (m²/s)", f"{res['kinematic_viscosity']:.3e}")

if delta_T > 0:
    st.info("Hot day: air is less dense, so the density altitude is higher than the "
            "pressure altitude. Engine power, lift and climb performance drop.")
elif delta_T < 0:
    st.info("Cold day: air is denser, so the density altitude is lower than the "
            "pressure altitude.")

# ------------------------------------------------------------------
# Tabs
# ------------------------------------------------------------------
tab_plots, tab_table, tab_theory, tab_check, tab_about = st.tabs(
    ["📈 Graphs", "📋 Table", "📘 How it works", "✅ Validation", "👥 About"])

# data for the plots (0 to 20 km)
alts = np.linspace(0, 20000, 201)
data = [isa.atmosphere(a, delta_T) for a in alts]
std_data = [isa.atmosphere(a, 0.0) for a in alts]

with tab_plots:
    plots = [
        ("Temperature (K)", "temperature_K", 1),
        ("Pressure (Pa)", "pressure_Pa", 1),
        ("Density (kg/m³)", "density", 1),
        ("Speed of sound (m/s)", "speed_of_sound", 1),
    ]
    cols = st.columns(2)
    for i, (title, key, _) in enumerate(plots):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[d[key] for d in std_data], y=alts / 1000,
                                 name="Standard day", line=dict(color="#1f77b4")))
        if delta_T != 0:
            fig.add_trace(go.Scatter(x=[d[key] for d in data], y=alts / 1000,
                                     name=f"ISA {delta_T:+d} °C", line=dict(color="#d62728", dash="dash")))
        fig.add_trace(go.Scatter(x=[res[key]], y=[h / 1000], mode="markers",
                                 name="Your altitude", marker=dict(size=11, color="black")))
        fig.add_hline(y=11, line_dash="dot", line_color="gray",
                      annotation_text="Tropopause (11 km)")
        fig.update_layout(title=title, xaxis_title=title, yaxis_title="Altitude (km)",
                          height=380, margin=dict(l=10, r=10, t=50, b=10),
                          legend=dict(orientation="h", y=-0.25))
        cols[i % 2].plotly_chart(fig, width="stretch")

with tab_table:
    rows = []
    for a in range(0, 20001, 1000):
        r = isa.atmosphere(a, delta_T)
        rows.append({
            "Altitude (m)": a,
            "Altitude (ft)": round(a / FT),
            "Temperature (K)": round(r["temperature_K"], 2),
            "Pressure (Pa)": round(r["pressure_Pa"], 1),
            "Density (kg/m³)": round(r["density"], 4),
            "Speed of sound (m/s)": round(r["speed_of_sound"], 2),
        })
    st.dataframe(rows, width="stretch", hide_index=True)
    st.download_button("Download table as CSV",
                       data="\n".join([",".join(rows[0].keys())] +
                                      [",".join(str(v) for v in r.values()) for r in rows]),
                       file_name="isa_table.csv", mime="text/csv")

with tab_theory:
    st.markdown(r"""
### Model used
The atmosphere is divided into two layers up to 20 km.

| Layer | Altitude | Temperature | Pressure |
|---|---|---|---|
| Troposphere | 0 – 11 km | $T = T_0 - 0.0065\,h$ | $P = P_0\left(\dfrac{T}{T_0}\right)^{g/(R\cdot 0.0065)}$ |
| Lower stratosphere | 11 – 20 km | $T = 216.65\ \text{K}$ | $P = P_{11}\,e^{-g(h-11000)/(RT)}$ |

**Constants:** $T_0 = 288.15$ K, $P_0 = 101325$ Pa, $g = 9.80665$ m/s², $R = 287.05$ J/(kg·K)

### Other quantities
- Density: $\rho = \dfrac{P}{RT}$
- Speed of sound: $a = \sqrt{\gamma R T}$ with $\gamma = 1.4$
- Dynamic viscosity (Sutherland): $\mu = 1.458\times10^{-6}\,\dfrac{T^{3/2}}{T+110.4}$

### Hot / cold day and density altitude
On a non-standard day the pressure at a given *pressure altitude* stays the same,
but the temperature is $T = T_{ISA} + \Delta T$. So the density changes:
$\rho = P / (R\,T)$.
**Density altitude** is the altitude in the *standard* atmosphere that has this same density.
Aircraft performance depends on density altitude, which is why airplanes
struggle on hot days at high airports.
""")

with tab_check:
    st.write("Calculated values compared with the published ISA table (standard day).")
    ref = [  # altitude m, T (K), P (Pa)
        (0, 288.15, 101325.0),
        (1000, 281.65, 89874.6),
        (5000, 255.65, 54019.9),
        (10000, 223.15, 26436.3),
        (11000, 216.65, 22632.1),
        (15000, 216.65, 12044.6),
        (20000, 216.65, 5474.9),
    ]
    check = []
    for a, t_ref, p_ref in ref:
        t_calc, p_calc = isa.isa_temperature(a), isa.isa_pressure(a)
        check.append({
            "Altitude (m)": a,
            "T table (K)": t_ref, "T calc (K)": round(t_calc, 2),
            "P table (Pa)": p_ref, "P calc (Pa)": round(p_calc, 1),
            "P error (%)": round(abs(p_calc - p_ref) / p_ref * 100, 3),
        })
    st.dataframe(check, width="stretch", hide_index=True)

with tab_about:
    st.subheader("About this project")
    st.write(
        "This web app calculates the properties of the International Standard "
        "Atmosphere up to 20 km and shows how hot or cold days change air density "
        "and density altitude. It was built as a mechanical engineering project "
        "related to the aviation sector."
    )
    st.markdown("#### Team")
    for member in TEAM_MEMBERS:
        st.markdown(f"- {member}")
    st.markdown(f"**{DEPARTMENT}**  \n{COLLEGE} ({YEAR})")
    if GUIDE:
        st.markdown(f"**Guide:** {GUIDE}")
    st.markdown(f"**Source code:** [{GITHUB_URL}]({GITHUB_URL})")
    st.markdown("#### Tools used")
    st.write("Python, Streamlit, NumPy, Plotly")

st.divider()
st.caption(f"Valid for 0–20 km, dry air, standard ISA model. Altitude input is treated "
           f"as pressure altitude.  |  © {TEAM_TEXT}")
