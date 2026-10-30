"""
isa.py - International Standard Atmosphere (ISA) calculations, 0 to 20 km.

Layers used:
  Troposphere        0 - 11 km : temperature falls linearly (lapse rate 6.5 K/km)
  Lower stratosphere 11 - 20 km: temperature is constant at 216.65 K
"""

import math

# ---- Constants (sea level standard) ----
T0 = 288.15        # K, sea level temperature
P0 = 101325.0      # Pa, sea level pressure
G = 9.80665        # m/s^2, gravitational acceleration
R = 287.05         # J/(kg.K), specific gas constant of air
GAMMA = 1.4        # ratio of specific heats for air
LAPSE = 0.0065     # K/m, temperature lapse rate in troposphere
H_TROPOPAUSE = 11000.0   # m
T_STRAT = 216.65         # K, temperature in lower stratosphere
RHO0 = P0 / (R * T0)     # kg/m^3, sea level density (about 1.225)

# Pressure at the tropopause (11 km), used for the stratosphere formula
P_TROPOPAUSE = P0 * (T_STRAT / T0) ** (G / (R * LAPSE))


def isa_temperature(h):
    """Standard temperature (K) at altitude h (m)."""
    if h <= H_TROPOPAUSE:
        return T0 - LAPSE * h
    return T_STRAT


def isa_pressure(h):
    """Standard pressure (Pa) at altitude h (m)."""
    if h <= H_TROPOPAUSE:
        return P0 * ((T0 - LAPSE * h) / T0) ** (G / (R * LAPSE))
    return P_TROPOPAUSE * math.exp(-G * (h - H_TROPOPAUSE) / (R * T_STRAT))


def isa_density(h):
    """Standard density (kg/m^3) at altitude h (m)."""
    return isa_pressure(h) / (R * isa_temperature(h))


def speed_of_sound(T):
    """Speed of sound (m/s) at temperature T (K)."""
    return math.sqrt(GAMMA * R * T)


def viscosity(T):
    """Dynamic viscosity (Pa.s) from Sutherland's formula."""
    return 1.458e-6 * T ** 1.5 / (T + 110.4)


def atmosphere(h, delta_T=0.0):
    """
    Return atmospheric properties at pressure altitude h (m).

    delta_T is the temperature deviation from standard (K or deg C difference).
    delta_T = 0 gives the standard day. delta_T = +15 is a hot day.
    Pressure follows the standard atmosphere (that is what pressure altitude
    means); temperature and density change with the deviation.
    """
    T = isa_temperature(h) + delta_T
    P = isa_pressure(h)
    rho = P / (R * T)
    a = speed_of_sound(T)
    mu = viscosity(T)
    return {
        "altitude_m": h,
        "temperature_K": T,
        "temperature_C": T - 273.15,
        "pressure_Pa": P,
        "density": rho,
        "speed_of_sound": a,
        "viscosity": mu,
        "kinematic_viscosity": mu / rho,
        "density_ratio": rho / RHO0,       # sigma
        "pressure_ratio": P / P0,          # delta
        "temperature_ratio": T / T0,       # theta
    }


def density_altitude(rho, h_low=-1000.0, h_high=20000.0):
    """
    Altitude (m) in the STANDARD atmosphere that has the given density.
    Found by bisection, because density always decreases with altitude.
    """
    for _ in range(100):
        mid = (h_low + h_high) / 2
        if isa_density(mid) > rho:
            h_low = mid      # standard density still too high -> go higher
        else:
            h_high = mid
    return (h_low + h_high) / 2
