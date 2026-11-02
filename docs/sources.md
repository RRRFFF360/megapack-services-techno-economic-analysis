# Sources and evidence register

Verified links on 2026-11-01; historical inputs retain the qualifications below.

1. [CAISO OASIS](https://oasis.caiso.com/) — 12 monthly PRC_LMP DAM exports for TH_NP15_GEN-APND, local operating year 2025. Recovered files are identified by filename and SHA-256 in `data/processed/raw_source_manifest.json`. Their filenames record retrieval on 2026-11-01. Total LMP rows are filtered separately from congestion, energy, loss and greenhouse-gas components.
2. [CAISO OASIS API specification](https://www.caiso.com/documents/oasisapispecification.pdf) — official documentation; a local copy was recovered. Use the original monthly exports or the documented OASIS query interface to retrieve PRC_LMP / DAM / TH_NP15_GEN-APND. Honor API interval limits; preserve CAISO operating-date semantics.
3. [Tesla Megapack](https://www.tesla.com/megapack) — official product and service positioning. It describes both Tesla servicing and certification of an in-house or third-party team. Customer-segment recommendations in this analysis are Richard's hypotheses, not Tesla's claims.
4. [Tesla Megapack Configurator](https://www.tesla.com/megapack/design) — prior study's reported configuration and price source. Original screenshots were not recovered. $9,099,280 hardware, $55,580 maintenance, 10 units, and 93.7% RTE are retained as user-provided historical study assumptions, not freshly observed quotes/specifications.
5. [2025 Annual Technology Baseline](https://atb.nlr.gov/) — background cost/performance benchmarking. Recovered workbook: `2025_v1_Workbook_08-27-2026.xlsx`. No workbook-derived parameter is used in the reconstructed cash-flow calculation. The workbook is not redistributed.
6. `reference_dispatch_2025.csv` — recovered original study output, formerly `megapack_dispatch_2025.csv`. Serves as an independent regression reference for this reconstruction. Original model scripts were unavailable.

Raw exports, workbook, official PDF, and unredacted screenshots are not redistributed. Processed public market data and the original study dispatch are included for transparent reproduction. Source marks belong to their owners; this repository does not claim ownership of external data.
