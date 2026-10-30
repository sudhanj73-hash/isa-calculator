# Standard Atmosphere (ISA) Calculator

A web app that calculates temperature, pressure, density, speed of sound and
viscosity of the International Standard Atmosphere from 0 to 20 km.

Extra features:
- Hot / cold day correction (temperature deviation from ISA)
- Density altitude
- Switchable units (m / ft / km, Pa / kPa / hPa / psi / atm, °C / K / °F)
- Graphs of every property versus altitude (standard day vs your day)
- Table with CSV download
- Validation tab comparing results with the published ISA table

## Files
| File | Purpose |
|---|---|
| `isa.py` | All the atmosphere calculations (no web code) |
| `app.py` | The Streamlit website (inputs, results, graphs) |
| `requirements.txt` | Python packages needed |

## Run on your computer
1. Install Python 3.9 or newer.
2. Open a terminal in this folder and run:
   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. Your browser opens at http://localhost:8501

## Put it online for free (Streamlit Community Cloud)
1. Create a free account at github.com and make a new repository.
2. Upload `app.py`, `isa.py`, `requirements.txt` and `README.md` to it.
3. Go to share.streamlit.io and sign in with GitHub.
4. Click **Create app**, choose your repository, set the main file to `app.py`, and click **Deploy**.
5. After a minute you get a public link you can share.

## Theory
- Troposphere (0-11 km): T = T0 - 0.0065 h, P = P0 (T/T0)^(g/(R*0.0065))
- Lower stratosphere (11-20 km): T = 216.65 K, P = P11 exp(-g (h - 11000) / (R T))
- Density: rho = P / (R T)
- Speed of sound: a = sqrt(1.4 R T)
- Viscosity: Sutherland's formula
- Density altitude: the standard-atmosphere altitude with the same density as the actual air

## Limits
Dry air, standard ISA model, valid up to 20 km. The altitude entered is treated as pressure altitude.
