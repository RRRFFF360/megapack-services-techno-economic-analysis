"""Audit generated outputs and independently re-solve all stored outage events."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'model'))
from dispatch_optimization import solve_day
from run_analysis import check_dispatch
from service_economics import pv_annuity

p = pd.read_csv(root/'data/processed/np15_da_lmp_2025.csv')
d = pd.read_csv(root/'data/processed/dispatch_2025.csv')
events = pd.read_csv(root/'analysis/outage_events.csv')
stamps = pd.to_datetime(p.timestamp_utc, utc=True)
assert p.notna().all().all() and d.notna().all().all()
assert np.isfinite(p.lmp_per_mwh).all()
assert len(p) == 8760 and stamps.is_unique
assert stamps.diff().dropna().eq(pd.Timedelta(hours=1)).all()
assert (stamps.dt.tz_convert('America/Los_Angeles').dt.strftime('%Y-%m-%d') == p.operating_date).all()
assert p.groupby('operating_date').size().value_counts().to_dict() == {24:363, 23:1, 25:1}
assert len(events) == 216 and len(events[events.duration_requested_hours==4]) == 96
assert not events.duplicated(['day_type','date','duration_requested_hours','start_interval_index']).any()
assert events.notna().all().all()
for event in events.itertuples():
    day = p[p.operating_date == event.date].reset_index(drop=True)
    n = len(day)
    start = event.start_interval_index
    end = n if event.duration_requested_hours == 24 else min(n, start+event.duration_requested_hours)
    mask = np.ones(n)
    mask[start:end] = 0
    counterfactual = solve_day(day, availability=mask)
    check_dispatch(counterfactual)
    assert (counterfactual.iloc[start:end].charge_mw.abs() < 1e-6).all()
    assert (counterfactual.iloc[start:end].discharge_mw.abs() < 1e-6).all()
    assert event.actual_outage_hours == end-start
    assert abs(counterfactual.hourly_market_value_usd.sum()-event.outage_day_da_value_usd) < 1e-5
    assert abs(event.base_day_da_value_usd-event.outage_day_da_value_usd-event.da_opportunity_loss_usd) < 1e-5
    assert event.da_opportunity_loss_usd >= -1e-6
    if event.duration_requested_hours == 24:
        assert abs(event.outage_day_da_value_usd) < 1e-5

cohort = pd.read_csv(root/'analysis/outage_summary.csv')
for row in cohort.itertuples():
    values = events[(events.day_type==row.day_type)&(events.duration_requested_hours==row.duration_requested_hours)].da_opportunity_loss_usd
    assert len(values) == row.sampled_events
    assert abs(values.median()-row.median_loss_usd) < 1e-8
    assert abs(values.max()-row.maximum_loss_usd) < 1e-8
summary = json.loads((root/'analysis/summary.json').read_text())
service = json.loads((root/'analysis/service_value_summary.json').read_text())
assert abs(d.hourly_market_value_usd.sum()-summary['annual_da_value_usd']) < 1e-5
cf = pd.read_csv(root/'analysis/15yr_real_dollar_economics.csv')
assert len(cf)==15
assert abs(cf.net_operating_pv_usd.sum()-summary['net_operating_pv_usd']) < 1e-5
assert abs(pv_annuity(20000)-service['15yr_pv_of_illustrative_20000_annual_service_premium_usd'])<1e-5
examples = pd.read_csv(root/'analysis/illustrative_service_scenarios.csv')
assert not examples.is_verified_provider_performance.any()
assert not examples.is_verified_comparable_quote.any()
assert np.allclose(examples.annual_service_plus_da_loss_usd, examples.annual_service_cost_usd+examples.annual_da_loss_usd)

result = {'status':'passed','hours':len(p),'local_days':365,'dst_hour_counts':{'24':363,'23':1,'25':1},
          'independently_resolved_outages':len(events),'annual_da_value_usd':summary['annual_da_value_usd'],
          'net_operating_pv_usd':summary['net_operating_pv_usd'],
          'four_hour_median_usd':service['median_loss_all_sampled_4h_events_usd'],
          'max_daily_reference_difference_usd':summary['max_daily_reference_difference_usd']}

print(json.dumps(result,indent=2))
