"""Reconstructed, AI-assisted daily MILP; not the unrecovered original script."""
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint

POWER_MW = 9.79
ENERGY_MWH = 39.16
RTE = 0.937

def solve_day(day, cycles=1.0, rte=RTE, availability=None):
    """Perfect-foresight daily MILP with optional hourly power-availability mask.

    availability[t]=0 prohibits both charging and discharging in hour t.
    This models a hypothetical outage, not a measured SLA or provider reliability.
    """
    n = len(day)
    if n not in (23,24,25):
        raise ValueError(f"Expected 23-25 local-day hours; received {n}")
    if availability is None:
        availability = np.ones(n)
    availability = np.asarray(availability, dtype=float)
    if availability.shape != (n,) or not np.isfinite(availability).all() or (availability < 0).any() or (availability > 1).any():
        raise ValueError("availability must have one [0,1] value per operating hour")
    if cycles < 0 or not 0 < rte <= 1:
        raise ValueError("Invalid cycles or RTE")
    eta = np.sqrt(rte)
    # Variables: AC charge[n], AC discharge[n], end-of-hour SOC[n], charge mode[n].
    objective = np.r_[day.lmp_per_mwh, -day.lmp_per_mwh, np.zeros(2*n)]
    upper = np.r_[POWER_MW*availability, POWER_MW*availability, np.full(n, ENERGY_MWH), np.ones(n)]
    rows, low, high = [], [], []
    def constraint(row, lower, upper):
        rows.append(row); low.append(lower); high.append(upper)
    for t in range(n):
        a = np.zeros(4*n); a[t] = -eta; a[n+t] = 1/eta; a[2*n+t] = 1
        if t: a[2*n+t-1] = -1
        rhs = ENERGY_MWH/2 if t == 0 else 0
        constraint(a, rhs, rhs)
        a = np.zeros(4*n); a[t] = 1; a[3*n+t] = -POWER_MW
        constraint(a, -np.inf, 0)
        a = np.zeros(4*n); a[n+t] = 1; a[3*n+t] = POWER_MW
        constraint(a, -np.inf, POWER_MW)
    a = np.zeros(4*n); a[3*n-1] = 1
    constraint(a, ENERGY_MWH/2, ENERGY_MWH/2)
    a = np.zeros(4*n); a[n:2*n] = 1/eta
    constraint(a, -np.inf, cycles*ENERGY_MWH)
    result = milp(objective, integrality=np.r_[np.zeros(3*n), np.ones(n)],
                  bounds=Bounds(np.zeros(4*n), upper),
                  constraints=LinearConstraint(np.array(rows), low, high),
                  options={'mip_rel_gap': 1e-8})
    if not result.success: raise RuntimeError(result.message)
    out = day.copy()
    out['charge_mw'] = result.x[:n]
    out['discharge_mw'] = result.x[n:2*n]
    out['soc_start_mwh'] = np.r_[ENERGY_MWH/2, result.x[2*n:3*n-1]]
    out['soc_end_mwh'] = result.x[2*n:3*n]
    out['hourly_market_value_usd'] = (out.discharge_mw-out.charge_mw)*out.lmp_per_mwh
    return out

def solve_year(prices, cycles=1.0, rte=RTE):
    return pd.concat([solve_day(g, cycles, rte) for _, g in prices.groupby('operating_date', sort=True)], ignore_index=True)
