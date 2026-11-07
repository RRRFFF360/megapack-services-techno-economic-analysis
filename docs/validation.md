# Release validation — 2026-11-06

Executed locally on Windows with Python 3.10.5 and all four pinned requirements. This records executed validation, not a claim about GitHub Actions.

## Commands and outcomes

| Command | Actual outcome |
| --- | --- |
| `python -m pip check` | No broken requirements |
| `python model/run_analysis.py` | Passed: full 365-day baseline, cycle/RTE sensitivities, cash flows, figures and 216 outage counterfactuals |
| `python model/plot_customer_segmentation.py` | Completed |
| `python -m unittest discover -s tests -v` | 7 tests passed |
| `python model/service_economics.py` | Standalone extension and data-driven outage chart regenerated successfully |
| `python model/validate_outputs.py` | Passed: independently re-solved all 216 stored outage events and reconciled outputs |

The full runner was executed before and after the numerical-input/test changes. The final chart serialization change was then checked through the standalone service runner, output audit and seven tests; it does not alter dispatch calculations.

## Verified outputs

- 8,760 unique continuous UTC hours; 365 Los Angeles operating days: 363 with 24 hours, one with 23 and one with 25.
- Annual DA value after charging purchases: **$375,384.0847597687**.
- 15-year operating PV after assumed maintenance: **$3,106,016.8984834948**.
- Maximum daily objective difference against preserved original dispatch: **$6.82e-13** in this environment. Equivalent optimal hourly schedules and machine-level CSV rounding may vary.
- 216 stored outage events; 96 four-hour events; median four-hour loss **$49.7694066869517**, sample maximum **$870.2901003563077**.
- Every event re-solved and checked for zero charge/discharge in disabled intervals, physical balances, SOC/power bounds, daily SOC closure, no simultaneous charge/discharge, cycle cap and stored objective/loss agreement.
- Cohort medians and maxima, cash-flow totals, illustrative fee PV and cost arithmetic reconciled. Every example-provider evidence flag remains false.
- Seven unit tests cover full outages, objective monotonicity, malformed/nonfinite masks, 23/25-hour days, partial derating, nonfinite model parameters and teaching-cost arithmetic.

## Release fixes

Added the previously untracked `analysis/outage_events.csv`, generated the outage figure directly from cohort results, rejected nonfinite cycle parameters, expanded tests and added a repeatable output audit. No validated economic conclusion changed.

## Evidence limits

The raw monthly CAISO exports are not distributed in this checkout, so raw-source ingestion and source-file hashes could not be independently re-created here. Included processed prices were checked against preserved hourly reference data. Historical Tesla hardware/configuration/RTE/maintenance inputs remain prior-study assumptions with unrecovered Configurator screenshots; they were not verified as current quotations. Outage timing and provider failure frequencies/cost comparisons are hypothetical, not Tesla field data. Perfect-foresight DA-only results are not expected revenue or complete project NPV/ROI/IRR.
