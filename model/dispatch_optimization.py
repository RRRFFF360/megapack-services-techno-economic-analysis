"""Reconstructed, AI-assisted daily MILP; not the unrecovered original script."""
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint

POWER_MW = 9.79
ENERGY_MWH = 39.16
RTE = 0.937

def solve_day(day, cycles=1.0, rte=RTE):
    """AC charge/discharge; symmetric efficiency; discharge/(eta*E) internal-energy cycle cap."""
    n = len(day)
    eta = np.sqrt(rte)
    # Variables: AC charge[n], AC discharge[n], end-of-hour SOC[n], charge mode[n].
    objective = np.r_[day.lmp_per_mwh, -day.lmp_per_mwh, np.zeros(2*n)]
    upper = np.r_[np.full(2*n, POWER_MW), np.full(n, ENERGY_MWH), np.ones(n)]
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
