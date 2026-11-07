"""Outage-timing counterfactuals and illustrative service economics.

Not an estimate of Tesla uptime, provider performance, or actual service quotes.
Re-run: python model/service_economics.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from dispatch_optimization import solve_day

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed'
ANALYSIS = ROOT / 'analysis'
YEARS = 15
REAL_DISCOUNT = .06
HISTORICAL_TESLA_MAINTENANCE_ESTIMATE_USD = 55580.
ILLUSTRATIVE_ANNUAL_PREMIUM_USD = 20000.


def pv_annuity(amount, rate=REAL_DISCOUNT, years=YEARS):
    return float(sum(amount/(1+rate)**year for year in range(1,years+1)))


def daily_da_value(day, availability=None):
    return float(solve_day(day, availability=availability).hourly_market_value_usd.sum())


def representative_days(prices, reference):
    """Two deliberately selected day types/month: median-value and highest-value."""
    daily = reference.groupby('operating_date').hourly_market_value_usd.sum()
    selected = []
    for month in range(1,13):
        candidate = daily[daily.index.str[:7] == f'2025-{month:02d}']
        if candidate.empty:
            raise ValueError(f'Missing month {month}')
        typical = (candidate-candidate.median()).abs().sort_values(kind='stable').index[0]
        highest = candidate.idxmax()
        selected += [('median_day',typical),('high_value_day',highest)]
    return selected


def simulate_outages(prices, reference):
    rows = []
    for day_type,date in representative_days(prices,reference):
        day = prices.loc[prices.operating_date==date].reset_index(drop=True)
        original = daily_da_value(day)
        stored = float(reference.loc[reference.operating_date==date,'hourly_market_value_usd'].sum())
        if abs(original-stored)>.05:
            raise AssertionError(f'Baseline DA objective mismatch on {date}: {original-stored}')
        n = len(day)
        for hours in (1,4,24):
            for start in ((0,) if hours==24 else (0,6,12,18)):
                end = n if hours==24 else min(start+hours,n)
                available = np.ones(n)
                available[start:end] = 0.
                after = daily_da_value(day,available)
                loss = original-after
                if loss < -.02:
                    raise AssertionError('An outage should not increase the optimum')
                rows.append(dict(month=date[:7],date=date,day_type=day_type,
                                 duration_requested_hours=hours,actual_outage_hours=end-start,
                                 start_interval_index=start,base_day_da_value_usd=original,
                                 outage_day_da_value_usd=after,
                                 da_opportunity_loss_usd=max(0.,loss)))
    return pd.DataFrame(rows)


def service_scenarios(event_loss_usd):
    """TEACHING-ONLY inputs, NOT quotes or verified outages for any provider."""
    examples = [
        ('Tesla-managed (illustrative)',HISTORICAL_TESLA_MAINTENANCE_ESTIMATE_USD,2.),
        ('Certified in-house (illustrative)',35000.,6.),
        ('Certified third-party (illustrative)',42000.,4.)
    ]
    results=[]
    for label,cost,frequency in examples:
        annual_loss=event_loss_usd*frequency
        burden=cost+annual_loss
        results.append(dict(service_path=label,annual_service_cost_usd=cost,
                            annual_four_hour_outages_assumed=frequency,
                            event_loss_assumed_usd=event_loss_usd,annual_da_loss_usd=annual_loss,
                            annual_service_plus_da_loss_usd=burden,
                            pv_15yr_burden_usd=pv_annuity(burden),
                            is_verified_provider_performance=False,
                            is_verified_comparable_quote=False))
    return pd.DataFrame(results)


def plot_outage_summary(cohort, output_path):
    """Regenerate the publication figure from calculated cohort statistics."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels = ['1 hour', '4 hours', 'Full local day']
    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.patch.set_facecolor('#fbfcf9')
    ax.set_facecolor('#fbfcf9')
    for offset, kind, color, label in [
        (-.18, 'median_day', '#14654b', 'Selected median-value days'),
        (.18, 'high_value_day', '#a87045', 'Selected high-value days')
    ]:
        values = cohort.loc[cohort.day_type == kind].set_index('duration_requested_hours').loc[[1,4,24], 'median_loss_usd']
        bars = ax.bar(np.arange(3)+offset, values, width=.34, color=color, label=label)
        ax.bar_label(bars, labels=[f'${value:,.2f}' for value in values], padding=4, fontsize=9)
    ax.set_xticks(range(3), labels)
    ax.set_ylabel('Median simulated DA-only loss ($/event)')
    ax.set_ylim(0, float(cohort.median_loss_usd.max())*1.3)
    ax.set_title('Outage timing changes DA-only exposure', loc='left', fontweight='bold')
    ax.legend(frameon=False, fontsize=9, loc='upper left')
    ax.spines[['top', 'right']].set_visible(False)
    fig.text(.09, .06, '216 purposefully selected counterfactuals; advance-known prices and outages.\nNot observed losses or provider reliability. Full day covers every local-day interval.', fontsize=9, color='#52625b')
    fig.tight_layout(rect=(0, .13, 1, 1))
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with plt.rc_context({'svg.fonttype': 'none', 'svg.hashsalt': 'megapack-outages'}):
        fig.savefig(output_path, metadata={'Date': None})
    plt.close(fig)
    if output_path.suffix == '.svg':
        output_path.write_text('\n'.join(line.rstrip() for line in output_path.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')


def run(prices_path=DATA/'np15_da_lmp_2025.csv',
        ref_path=DATA/'reference_dispatch_2025.csv',output_dir=ANALYSIS):
    prices = pd.read_csv(prices_path)
    ref = pd.read_csv(ref_path)
    if len(prices)!=8760 or len(ref)!=8760:
        raise ValueError('Expected 8760 prices and reference dispatch hours')
    events = simulate_outages(prices,ref)
    cohort = (events.groupby(['day_type','duration_requested_hours'],as_index=False)
              .agg(sampled_events=('da_opportunity_loss_usd','size'),
                   minimum_loss_usd=('da_opportunity_loss_usd','min'),
                   median_loss_usd=('da_opportunity_loss_usd','median'),
                   mean_loss_usd=('da_opportunity_loss_usd','mean'),
                   maximum_loss_usd=('da_opportunity_loss_usd','max')))
    four_hour_median = float(events.loc[events.duration_requested_hours==4,'da_opportunity_loss_usd'].median())
    example = service_scenarios(four_hour_median)
    summary = {
        'method':'retrospective daily perfect-foresight outage counterfactual; single-day outages only',
        'sample_design':'monthly median DA-value and high-value day, start intervals 0/6/12/18; not random',
        'outage_events_tested':len(events),
        'median_loss_all_sampled_4h_events_usd':four_hour_median,
        '15yr_pv_of_illustrative_20000_annual_service_premium_usd':pv_annuity(ILLUSTRATIVE_ANNUAL_PREMIUM_USD),
        'four_hour_events_avoided_each_year_to_cover_illustrative_premium_da_only':
            ILLUSTRATIVE_ANNUAL_PREMIUM_USD/four_hour_median if four_hour_median>0 else None,
        'historical_tesla_maintenance_estimate_usd':HISTORICAL_TESLA_MAINTENANCE_ESTIMATE_USD,
        'all_provider_performance_cost_assumptions_illustrative':True,
        'notes':[
            'Outage mask prohibits AC charge and discharge; the model shifts other feasible hours.',
            'Assuming an advance-known outage may understate losses of unexpected failures.',
            'Purposeful sample and outage-rate extrapolation are thought experiments, not forecasts.',
            'DA-only omits contracted capacity, ancillary services, penalties, safety, repair and warranty effects.',
            'No provider rank is supportable without real reliability data and matched-scope quotes.'
        ]
    }
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    events.to_csv(output_dir/'outage_events.csv',index=False)
    cohort.to_csv(output_dir/'outage_summary.csv',index=False)
    example.to_csv(output_dir/'illustrative_service_scenarios.csv',index=False)
    (output_dir/'service_value_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    plot_outage_summary(cohort, ROOT/'figures'/'outage_opportunity_loss.svg')
    return events,cohort,example,summary


if __name__=='__main__':
    _,table,examples,summary=run()
    print(table.to_string(index=False))
    print(examples.to_string(index=False))
    print(json.dumps(summary,indent=2))
