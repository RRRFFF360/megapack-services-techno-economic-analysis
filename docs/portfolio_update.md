# Portfolio page replacement — Megapack Services

**Suggested page title:** Megapack Services: Translating Battery Dispatch Economics Into B2B Service Decisions

**Subtitle:** Built a 2025 CAISO day-ahead battery dispatch model, then re-optimized 216 assumed outage scenarios to identify when uptime matters economically—and what a service recommendation must actually prove.

## Problem

How should a storage owner compare Tesla-managed maintenance with certified in-house or third-party delivery? A service invoice alone misses lost trading value, contract risk, repair quality, coverage and internal operating capability.

## What I built

- **Market baseline:** 8,760 hours of 2025 CAISO NP15 day-ahead prices; a 9.79 MW / 39.16 MWh modeled Megapack configuration; MILP charge/discharge optimization with 93.7% round-trip efficiency, SOC and cycle constraints.
- **Long-term economic context:** $375,384/year modeled DA-only value after charging purchases and $3.106M 15-year net operating PV under constant real-dollar assumptions and 6% real discount. This is **not** project NPV or ROI.
- **New outage experiment:** 216 hypothetical 1h, 4h and full-day power-availability masks across deliberately selected median/high-value days. Re-optimized remaining hours instead of assuming outages remove an average fraction of sales.
- **Service decision framework:** Price a service's **incremental avoided losses** against its **fully loaded incremental fee**, evaluating customer service capability, response/repair coverage, other market revenues and contract obligations.

## What the experiment found

Across 96 purposively sampled four-hour outages, the median loss in optimized **DA-only** opportunity was **$49.77**; some cases cost $0, while the sample maximum was **$870.29**. A hypothetical $20K/year premium would need to avoid ~402 of those median-sized events annually to pay for itself **from DA value alone**. This is *not* a prediction about real-world downtime and **not** evidence that maintenance is unimportant. It shows why DA arbitrage alone cannot justify an actual service recommendation.

## Product insight

**Service value depends on the customer's complete exposure, not simple uptime percentage.** Prioritize a service-value calculator using actual outage history, merchant + contracted revenue, response/restoration requirements, matched bids, staffing capability, spare parts and warranty coverage. Compare Tesla-serviced, Tesla-certified in-house and Tesla-certified third-party delivery paths; do not claim one provider inherently delivers higher availability.

## My role and what remains

Defined the commercial question, assembled and validated historical market inputs, selected model assumptions, used AI-assisted Python optimization and interpreted quantitative scenarios as B2B product hypotheses. Future validation: measured service/repair outcomes, provider bids, contract penalties, customer interviews and joint optimization of DA + other revenue stacks.

**Independent educational analysis** — not affiliated with Tesla. Hypothetical outage timing, reliability frequencies and illustrative service costs are **not** actual Tesla or third-party performance/quotes.

**Explore:** [GitHub code and dataset](https://github.com/RRRFFF360/megapack-services-techno-economic-analysis) · [Service-value methodology](https://github.com/RRRFFF360/megapack-services-techno-economic-analysis/blob/main/docs/service_value.md).
