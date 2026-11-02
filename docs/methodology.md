# Methodology

This is a retrospective optimization study, not machine learning or price forecasting.

## Data and time

Filter 12 original CAISO OASIS PRC_LMP monthly exports to `NODE=TH_NP15_GEN-APND`, `MARKET_RUN_ID=DAM`, `LMP_TYPE=LMP`. Use `MW` as the price value in this price report (USD/MWh, despite the generic column name). Retain operating date/hour and UTC interval start; sort by UTC and require one unique contiguous hourly record. The series covers the 2025 local operating year: 2025-01-01 08:00 UTC through 2026-01-01 07:00 UTC inclusive. Daylight saving creates one 23-hour day and one 25-hour day; neither is padded or dropped. The remaining 363 days have 24 hours. The aggregate trading hub is a proxy, not a site's interconnection node.

## Dispatch

Optimize each local operating day independently. Let c and d be AC charge/discharge MW, s be stored energy MWh, p be USD/MWh, and Δt=1 hour. Maximize Σ p(d−c)Δt. This subtracts charging purchases from discharging sales; it is not gross sales or full operating profit.

- P=9.79 MW; E=39.16 MWh. Display rounded as 9.8 MW / 39.2 MWh.
- η_charge=η_discharge=√0.937; thus η_charge × η_discharge=93.7%.
- s_end=s_start+η_charge cΔt−dΔt/η_discharge.
- 0≤s≤E; 0≤c,d≤P.
- Binary charge mode prevents simultaneous charging and discharging (also when prices are negative).
- Start and end each local day at E/2. Interday arbitrage is excluded.
- Σ(dΔt/η_discharge)≤cycles_per_day×E. Equivalent full cycles are measured on **internal discharged energy**, not AC exports. The default is 1 per day, including DST days.
- The full 0–100% modeled energy range is permitted. No additional SOC reserve/window is imposed.

SciPy `milp` / HiGHS solves the daily mixed-integer linear program at relative MIP gap 1e−8. Alternative optimal hourly schedules can differ while yielding equal daily value. Sensitivities re-optimize all days with only the stated parameter changed.

## Real-dollar operating economics

Hold annual 2025 modeled DA value and annual maintenance ($55,580) constant in real dollars for 15 years. Discount end-of-year net cash flow at 6% real. No nominal escalation is mixed with this real discount rate. The source currency price years were not independently reconciled; this is a constant-dollar scenario using supplied estimates, not an inflation-adjusted quote. `PV=Σ (annual_DA_value−maintenance)/(1+r)^year`. Sensitivities vary annual DA value by 0.8/1.0/1.2 and the real discount rate by 4/6/8%.

This is **operating PV before initial investment**, not project NPV. The $9,099,280 hardware comparison excludes installation, site-specific interconnection and other balance-of-plant costs. The percentage comparison is not an investment return or a payback calculation. No degradation, augmentation, residual value, or major replacement is embedded in this reconstructed constant-cash-flow model.

## Availability

1 percentage point × annual DA value is a first-order proportional approximation. It assumes lost availability has average economic exposure and does not model outage timing, recovery, contract penalties or nonlinear dispatch effects. This amount is neither an SLA quote nor a defensible standalone service price.

## Reproduction provenance

The original Python scripts and real-dollar result CSVs cited in the prior chat were not available in this workspace. The implementation here was reconstructed with AI assistance from documented assumptions and validated against the recovered original hourly dispatch file. Input prices match the 12 raw source exports exactly. The validation checks physics, no simultaneous charge/discharge, cycle limits, daily boundaries, price integrity and daily objective agreement with the original output. See `analysis/summary.json` for the measured maximum daily objective difference. This is a validated reconstruction, not a claim to have recovered the original source code.
