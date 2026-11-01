# Megapack Services Techno-Economic Analysis

**How do battery performance and service availability translate into customer economics?**

An independent PM case study using 8,760 hours of 2025 CAISO NP15 Day-Ahead prices, a 10-unit Megapack study configuration, and Python-assisted constrained optimization.

[Read the PM case study](https://richardfu.a2843668904.chatgpt.site/projects/megapack/) · [Methodology](docs/methodology.md) · [Assumptions](docs/assumptions.md) · [Sources](docs/sources.md) · [Limitations](docs/limitations.md)

## Key results

| Measure | Reproduced result |
|---|---:|
| Modeled power / energy | 9.79 MW / 39.16 MWh (rounded: 9.8 / 39.2) |
| Historical hourly prices | 8,760 |
| Annual DA value, after charging purchases | $375,384 |
| Base round-trip efficiency | 93.7% |
| 15-year DA operating PV, net of maintenance | $3,106,017 |
| PV / historical $9,099,280 hardware estimate | 34.1% |
| 1 pp availability, proportional DA-value approximation | $3,754/year |

**DA arbitrage is a narrow value baseline, not complete project valuation.** “Value floor” describes the limited revenue scope, not guaranteed realized revenue: perfect foresight can overstate achievable value within that scope. The operating PV excludes initial investment and must not be called project NPV.

## Role and contribution

Richard designed the analysis around the customer economics question, sourced and validated public data, defined operating assumptions and constraints, and used Python-assisted optimization. The contribution centers on interpreting quantitative evidence for product and service decisions. It does not claim independent hand-written development of a complex optimizer.

The original hourly output and all 12 raw monthly CAISO files were recovered. The original Python source was unavailable; this repository contains an explicitly documented **AI-assisted reconstruction**, validated against the original daily economic results. Maximum daily objective difference: under $0.000001. Hourly schedules may differ at equivalent optima.

## Market opportunity

Mean LMP was $38.23/MWh; 288 hours had negative prices; mean daily high–low spread was $35.13/MWh. The model values the timing of spreads subject to battery constraints, rather than treating average price as revenue.

![Observed example dispatch](figures/sample_dispatch.png)
![Monthly DA value](figures/monthly_arbitrage_value.png)

## Method and sensitivities

The daily MILP maximizes discharge sales less charging purchases, with power/energy limits, symmetric efficiency losses, mutually exclusive charge/discharge, and 50% starting/ending SOC. Default daily equivalent full cycles are capped at 1 on an **internal discharged energy** basis. Preserve the 23/25-hour daylight-saving days.

| Maximum daily cycles | Annual DA value |
|---|---:|
| 0.5 | $222,619 |
| 1.0 | $375,384 |
| 1.5 | $396,351 |
| 2.0 | $399,260 |

One daily cycle captures 94.0% of the value modeled with a two-cycle cap. Additional cycling has diminishing value before considering wear.

![Cycle sensitivity](figures/cycle_sensitivity.png)

| RTE | Annual DA value |
|---|---:|
| 90% | $354,041 |
| 92% | $365,666 |
| 93.7% | $375,384 |
| 95% | $382,716 |
| 96% | $388,298 |

93.7% versus 90% adds about $21,343/year in modeled DA value, holding other assumptions fixed.

![Efficiency sensitivity](figures/efficiency_sensitivity.png)

## Fifteen-year real-dollar scenario

Repeat annual modeled DA value and $55,580 annual maintenance in constant real dollars; discount year-end cash flows at 6% real for 15 years. DA value PV is $3.646M, maintenance PV $0.540M, and net operating PV $3.106M. This is 34.1% of the supplied historical hardware estimate, not a return on investment. Historical price years were not independently reconciled, and no degradation/augmentation or replacement schedule is modeled. See the [cash flows](analysis/15yr_real_dollar_economics.csv) and [scenario sensitivity](analysis/real_dollar_sensitivity.csv).

## Product implications

- **Frame services around total customer value protected.** DA uptime alone is too narrow to support a service-price conclusion. Contract performance, broader revenue streams, asset health, warranty/failure risk, and lifetime costs matter.
- **Segment by operating capability and downtime exposure.** Tesla servicing may suit owners seeking outsourced operational execution; certification may suit owners with capable internal or third-party teams. These are hypotheses to validate with customers, not demonstrated segment preferences.
- **Balance utilization against asset health.** Small marginal DA gains beyond one cycle motivate a lifecycle tradeoff assessment; this model does not quantify the wear cost.
- **Proposed framing:** an availability/performance-focused discussion based on total economic exposure. This is not a claim that Tesla offers an additional service tier.

## Reproduce

Tested with Python 3.9.6 and the pinned packages below. No network access is required after installation; processed prices are included.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python model/run_analysis.py
```

The run regenerates hourly dispatch, monthly results, cycle/efficiency sensitivities, real-dollar scenarios, four figures, and `analysis/summary.json`. It checks data continuity, price agreement, physical balances, SOC/power bounds, no simultaneous charging/discharging, cycle caps, and daily objective agreement against the preserved original output. A failed check stops the run. See [raw-data reconstruction](data/README.md).

```text
model/             data preparation, dispatch, real-dollar economics, full analysis
 data/processed/   hourly prices, original reference, regenerated outputs, source hashes
analysis/          sensitivity tables, 15-year cash flows, numerical summary
figures/           four regenerated analytical charts
docs/              methodology, assumptions, sources, limitations
```

## Limitations and source integrity

Perfect foresight; DA only; no RT, ancillary, RA, PPA/tolling, taxes, financing or site-specific interconnection. No full degradation, additional SOC reserve, augmentation or warranty-cost model. Availability is a proportional approximation, not outage simulation. NP15 is a hub proxy. Other revenue streams may compete for the same physical capacity and must not be added without co-optimization.

Hardware, maintenance, configuration and RTE retain the prior study's user-provided assumptions; Configurator screenshots were not recovered, and these are not current verified quotations. The recovered ATB workbook is background only, not an input to the reproduced constant-dollar cash flow. Full [evidence register](docs/sources.md) and [limitations](docs/limitations.md).

Independent educational project. Not affiliated with or endorsed by Tesla or CAISO.
