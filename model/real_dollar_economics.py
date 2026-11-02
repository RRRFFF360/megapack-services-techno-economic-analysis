"""Constant real annual DA value less constant real maintenance; year-end cash flow."""
import pandas as pd

def cashflows(annual_value, discount=0.06, maintenance=55580.0, years=15, revenue_factor=1.0):
    rows = []
    for y in range(1, years+1):
        revenue = annual_value*revenue_factor
        factor = 1/(1+discount)**y
        rows.append(dict(year=y,da_value_real_usd=revenue,maintenance_real_usd=maintenance,
                         net_operating_real_usd=revenue-maintenance,discount_factor=factor,
                         da_pv_usd=revenue*factor,maintenance_pv_usd=maintenance*factor,
                         net_operating_pv_usd=(revenue-maintenance)*factor))
    return pd.DataFrame(rows)
