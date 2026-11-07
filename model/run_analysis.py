"""Run from any directory: python model/run_analysis.py. Outputs stay in this repo."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dispatch_optimization import solve_year, POWER_MW, ENERGY_MWH, RTE
from real_dollar_economics import cashflows
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed'; ANALYSIS=ROOT/'analysis'; FIG=ROOT/'figures'
for directory in (DATA,ANALYSIS,FIG): directory.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'#fbfcf9','axes.facecolor':'#fbfcf9','savefig.facecolor':'#fbfcf9'})
GREEN='#14654b'; INK='#172c25'

def check_dispatch(d, cycles=1., rte=RTE):
    eta=np.sqrt(rte); tol=1e-5
    assert (d.charge_mw>=-tol).all() and (d.discharge_mw>=-tol).all()
    assert d.charge_mw.max()<=POWER_MW+tol and d.discharge_mw.max()<=POWER_MW+tol
    assert (d.soc_end_mwh>=-tol).all() and d.soc_end_mwh.max()<=ENERGY_MWH+tol
    assert np.max(np.minimum(d.charge_mw,d.discharge_mw))<tol
    assert np.max(abs(d.soc_end_mwh-d.soc_start_mwh-eta*d.charge_mw+d.discharge_mw/eta))<tol
    assert np.max(abs(d.hourly_market_value_usd-(d.discharge_mw-d.charge_mw)*d.lmp_per_mwh))<tol
    for _,g in d.groupby('operating_date'):
        assert abs(g.soc_start_mwh.iloc[0]-ENERGY_MWH/2)<tol
        assert abs(g.soc_end_mwh.iloc[-1]-ENERGY_MWH/2)<tol
        assert np.allclose(g.soc_start_mwh.iloc[1:],g.soc_end_mwh.iloc[:-1],atol=tol)
        assert g.discharge_mw.sum()/eta<=cycles*ENERGY_MWH+tol

def save(name):
    plt.tight_layout(); plt.savefig(FIG/(name+'.png'),dpi=180); plt.close()

def bars(frame,x,name,title,xlabel):
    fig,ax=plt.subplots(figsize=(8,4.5)); vals=frame.annual_da_value_usd/1000
    bars=ax.bar(frame[x].astype(str),vals,color=GREEN,width=.6)
    ax.bar_label(bars,labels=[f'${v:,.1f}K' for v in vals],padding=7)
    ax.set(title=title,xlabel=xlabel,ylabel='Annual DA value ($ thousands)',ylim=(0,max(vals)*1.2))
    save(name)

def main():
    p=pd.read_csv(DATA/'np15_da_lmp_2025.csv'); ref=pd.read_csv(DATA/'reference_dispatch_2025.csv')
    stamps=pd.to_datetime(p.timestamp_utc,utc=True)
    assert len(p)==8760 and stamps.is_unique and stamps.diff().dropna().eq(pd.Timedelta(hours=1)).all()
    assert (stamps.to_numpy()==pd.to_datetime(ref.timestamp_utc,utc=True).to_numpy()).all()
    assert np.allclose(p.lmp_per_mwh,ref.lmp_per_mwh,atol=1e-10)
    base=solve_year(p); check_dispatch(base); check_dispatch(ref)
    annual=float(base.hourly_market_value_usd.sum())
    daily_difference=float((base.groupby('operating_date').hourly_market_value_usd.sum()-ref.groupby('operating_date').hourly_market_value_usd.sum()).abs().max())
    assert daily_difference<.05, f'Daily reference mismatch: {daily_difference}'
    base.to_csv(DATA/'dispatch_2025.csv',index=False)
    monthly=base.assign(month=base.operating_date.str[:7]).groupby('month').agg(charge_mwh=('charge_mw','sum'),discharge_mwh=('discharge_mw','sum'),da_value_usd=('hourly_market_value_usd','sum')).reset_index()
    monthly.to_csv(DATA/'monthly_summary_2025.csv',index=False)
    cycle=[]
    for value in [.5,1,1.5,2]:
        d=base if value==1 else solve_year(p,cycles=value); check_dispatch(d,cycles=value)
        cycle.append(dict(cycles_per_day=value,annual_da_value_usd=d.hourly_market_value_usd.sum()))
    cycle=pd.DataFrame(cycle); cycle.to_csv(ANALYSIS/'cycle_sensitivity.csv',index=False)
    efficiency=[]
    for value in [.90,.92,.937,.95,.96]:
        d=base if value==RTE else solve_year(p,rte=value); check_dispatch(d,rte=value)
        efficiency.append(dict(rte_percent=value*100,annual_da_value_usd=d.hourly_market_value_usd.sum()))
    efficiency=pd.DataFrame(efficiency); efficiency.to_csv(ANALYSIS/'efficiency_sensitivity.csv',index=False)
    cf=cashflows(annual); cf.to_csv(ANALYSIS/'15yr_real_dollar_economics.csv',index=False)
    sensitivity=[dict(real_discount_rate=rate,revenue_factor=rf,net_operating_pv_usd=cashflows(annual,discount=rate,revenue_factor=rf).net_operating_pv_usd.sum()) for rate in [.04,.06,.08] for rf in [.8,1,1.2]]
    pd.DataFrame(sensitivity).to_csv(ANALYSIS/'real_dollar_sensitivity.csv',index=False)
    daily=p.groupby('operating_date').lmp_per_mwh.agg(['max','min'])
    summary=dict(hour_count=len(p),power_mw=POWER_MW,energy_mwh=ENERGY_MWH,rte=RTE,annual_da_value_usd=annual,mean_lmp_usd_per_mwh=float(p.lmp_per_mwh.mean()),negative_price_hours=int((p.lmp_per_mwh<0).sum()),mean_daily_spread_usd_per_mwh=float((daily['max']-daily['min']).mean()),net_operating_pv_usd=float(cf.net_operating_pv_usd.sum()),da_pv_usd=float(cf.da_pv_usd.sum()),maintenance_pv_usd=float(cf.maintenance_pv_usd.sum()),hardware_estimate_usd=9099280,hardware_coverage_ratio=float(cf.net_operating_pv_usd.sum()/9099280),availability_1pp_da_value_usd=annual*.01,max_daily_reference_difference_usd=daily_difference)
    (ANALYSIS/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    bars(cycle,'cycles_per_day','cycle_sensitivity','More cycling, diminishing marginal value','Daily internal discharge / energy capacity')
    bars(efficiency,'rte_percent','efficiency_sensitivity','Efficiency translates into customer value','Round-trip efficiency (%)')
    fig,ax=plt.subplots(figsize=(9,4.5)); ax.bar(monthly.month.str[-2:],monthly.da_value_usd/1000,color=GREEN); ax.set(title='2025 NP15 Day-Ahead arbitrage value',xlabel='Month',ylabel='DA value ($ thousands)'); save('monthly_arbitrage_value')
    # Deterministic illustrative observed day: nearest to median daily value among negative-price days.
    negdays=p.loc[p.lmp_per_mwh<0,'operating_date'].unique(); values=base.groupby('operating_date').hourly_market_value_usd.sum(); subset=values.loc[negdays]; sample=(subset-subset.median()).abs().idxmin(); day=base[base.operating_date==sample]
    fig,ax=plt.subplots(figsize=(9,4.5)); x=np.arange(len(day)); ax.bar(x,-day.charge_mw,color='#93b9ab',label='Charge'); ax.bar(x,day.discharge_mw,color=GREEN,label='Discharge'); ax.set(xlabel='Operating interval (local day)',ylabel='AC power (MW)',title=f'Observed dispatch example · {sample}'); ax.axhline(0,color=INK,lw=.6)
    right=ax.twinx(); right.plot(x,day.lmp_per_mwh,color='#b85b36',lw=2,label='LMP'); right.set_ylabel('LMP ($/MWh)'); ax.legend(loc='upper left',frameon=False); right.legend(loc='upper right',frameon=False); save('sample_dispatch')
    from service_economics import run as run_service_economics
    _, _, _, service_result = run_service_economics()
    print(f"Service counterfactuals: {service_result['outage_events_tested']} events", flush=True)
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__': main()
