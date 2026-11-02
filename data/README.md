# Data

`processed/np15_da_lmp_2025.csv` contains 8,760 unique contiguous hourly total LMP prices (USD/MWh). Source: CAISO OASIS, report PRC_LMP, market DAM, node TH_NP15_GEN-APND. Local operating dates are 2025-01-01–2025-12-31. Preserve UTC timestamps for uniqueness across daylight saving.

- `reference_dispatch_2025.csv`: recovered original study output; do not overwrite.
- `dispatch_2025.csv`: regenerated dispatch; equivalent optimal schedules can differ.
- `monthly_summary_2025.csv`: regenerated monthly charging, discharging and net DA market value.
- `raw_source_manifest.json`: names and SHA-256 hashes of the 12 original monthly exports.

## Optional reconstruction from raw monthly files

Place the 12 matching CAISO CSVs in a local ignored `data/raw/` directory, then run from repository root:

```sh
python model/prepare_data.py data/raw
python model/run_analysis.py
```

The cleaner filters total LMP only (not the component rows), checks continuity and DST day lengths, and sorts by UTC. The supplied processed file is sufficient for the standard reproduction; no credentials or network access are needed.
