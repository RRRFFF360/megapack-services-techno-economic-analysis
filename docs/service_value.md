# From dispatch economics to service value

## Decision problem

What does outage *timing* cost the customer, and under which customer-specific costs and service outcomes would a maintenance delivery path make sense? This independent PM study evaluates **incremental customer economics**, not provider reputation or a quoted Tesla service guarantee.

## New experiment: 216 hourly outage counterfactuals

The earlier 1-percentage-point availability shortcut assigned 1% of annual DA value ($3,754) to every 1 pp of availability. That is a uniform-loss simplification. The new `model/service_economics.py` makes each selected outage hour unavailable to **both charging and discharging**, and then re-optimizes every other hour of the affected local day. The value loss is the baseline daily DA optimum minus the constrained optimum. It is not the sum of the original schedules' earnings in the disabled hours; the battery can shift transactions.

It retains the 9.79 MW / 39.16 MWh, 93.7% RTE, one internal-discharge EFC/day, 50%-to-50% SOC and historical CAISO 2025 NP15 DAM price constraints. A perfect-foresight optimization assumes foreknowledge of prices and outages.

For each month, we choose the day nearest that month's **median baseline DA trading value** and the **highest baseline DA value**. For each, we simulate 1-hour and 4-hour outages starting at interval indexes 0, 6, 12 and 18, plus a full-local-day outage. This is 24 selected day-types × 9 test conditions = **216** event cases. A full-day event removes all 23–25 intervals if a selected day falls on daylight-saving changeover. The selection is deterministic and **not a probability sample**.

| Selected local-day cohort | Duration | Cases | Median DA-only loss | Sample maximum |
|---|---|---:|---:|---:|
| Median-value day | 1 hour | 48 | $9.98 | $128.77 |
| High-value day | 1 hour | 48 | $10.74 | $273.31 |
| Median-value day | 4 hours | 48 | $42.74 | $776.16 |
| High-value day | 4 hours | 48 | $58.10 | $870.29 |
| Median-value day | Full local day | 12 | $885.50 | $1,684.21 |
| High-value day | Full local day | 12 | $1,645.67 | $3,175.40 |

Across all **96 deliberately sampled 4h events**, the **unweighted median is $49.77** and some losses are $0. These are modeled DA opportunities, **not observed outage losses, expected site reliability, or Tesla service economics**. Outages that arrive unexpectedly, prevent planned transactions, or trigger capacity/ancillary/tolling penalties can cost more.

## The incremental decision: service fee versus avoided loss

The historical configuration uses a **$55,580 annual Tesla maintenance estimate with unverified scope**. We do not have comparable in-house and certified third-party quotes or observed provider-specific outage frequency and duration. As a transparent *thought experiment*, a hypothetical **$20,000/year incremental fee** would require avoiding about **402 of the sampled median-size four-hour outages per year** to pay for itself from **DA trading value alone** ($20,000/$49.77). Its 15-year real 6%-discounted fee PV is $194,245. This intentionally stark example illustrates the revenue-scope gap; it **does not** show real maintenance is uneconomic.

The file `analysis/illustrative_service_scenarios.csv` supplies an optional calculation exercise using **fabricated, labeled** cost and four-hour-event-rate assumptions for Tesla-managed, certified in-house and certified third-party delivery. The numbers are **not quotes, measured outage frequencies, warranties or rankings** and must not drive actual procurement. The historical Tesla number is also not a currently verified quote.

Use customer-specific data instead:

**Incremental service value = reduced DA opportunity loss + reduced other settlements/contract penalties + reduced repair and operational risk costs − incremental fully loaded service cost.**

Use matched service scopes, real rates and outages, and consistent real-dollar discounting. Prevent double counting gross settlements, avoided charging costs, penalty payments, and downtime losses.

## Practical PM recommendations

1. **Intake:** Collect the site's revenue stack (DA, RT, ancillary, resource adequacy, tolling), penalty exposure, historical outage timing/duration, internal certified team capability and repair coverage.
2. **Quantify:** Compare matched-scope service alternatives using hourly counterfactuals, provider quotes, restoration terms, spare parts, technician coverage, warranty exclusions and safety constraints.
3. **Segment:** High exposure requires stronger response and restoration **under any qualified provider**, not automatically Tesla; limited internal capability makes outsourced options more attractive but does not identify the better provider.
4. **Validate before launch:** Acquire real customer interview data, measured MTTR/outage histories, matched proposals and contract terms before claiming any reliability advantage, package price or willingness to pay.

These are **three analytical delivery paths** (Tesla-serviced; Tesla-certified in-house; Tesla-certified third-party), not three newly launched official Tesla subscription tiers.

## Reproduce and audit

Run `python model/run_analysis.py` (full original analysis + service extension), or `python model/service_economics.py` (only extension), and `python -m unittest discover -s tests -v`.

- `analysis/outage_events.csv` – 216 individual events (regenerated; not source market data)
- `analysis/outage_summary.csv` – cohort statistics
- `analysis/illustrative_service_scenarios.csv` – unverified teaching examples
- `analysis/service_value_summary.json` – assumptions, summary and a break-even calculation

**Limitations:** Retrospective perfect foresight, pre-known outages, local-day boundaries, 50% start/end SOC, fixed cycling ceiling, purposive date/start-time selection, DA-only NP15 hub pricing, no multi-day failure/restoration simulation, no degradation or warranty SOC restrictions, no actual Tesla/third-party reliability, no matched bids or customer economics. Other revenue streams must be **co-optimized** rather than added to the same MW without constraints. Full portfolio/IRR analysis needs CAPEX, interconnection, insurance, tax, augmentation and finance.

Related references: [Methodology](methodology.md) · [Assumptions](assumptions.md) · [Sources](sources.md) · [Limitations](limitations.md). AI-assisted scenario implementation, tested against preserved original dispatch daily values for the selected dates.
