"""Optional re-import of the 12 original CAISO monthly CSVs."""
import argparse, hashlib, json
from pathlib import Path
import pandas as pd

def prepare(raw_dir, output):
    files = sorted(Path(raw_dir).glob('*PRC_LMP_DAM*.csv'))
    if len(files) != 12: raise ValueError('Expected 12 monthly source CSVs')
    raw = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    p = raw.loc[(raw.NODE=='TH_NP15_GEN-APND') & (raw.MARKET_RUN_ID=='DAM') & (raw.LMP_TYPE=='LMP'),
                ['INTERVALSTARTTIME_GMT','OPR_DT','OPR_HR','MW']].copy()
    p.columns = ['timestamp_utc','operating_date','operating_hour','lmp_per_mwh']
    p.timestamp_utc = pd.to_datetime(p.timestamp_utc, utc=True)
    p = p.sort_values('timestamp_utc').reset_index(drop=True)
    assert len(p) == 8760 and p.timestamp_utc.is_unique
    assert p.timestamp_utc.diff().dropna().eq(pd.Timedelta(hours=1)).all()
    assert p.operating_date.min()=='2025-01-01' and p.operating_date.max()=='2025-12-31'
    assert p.groupby('operating_date').size().value_counts().to_dict()=={24:363,23:1,25:1}
    assert p.notna().all().all()
    output = Path(output); output.parent.mkdir(parents=True, exist_ok=True)
    p.to_csv(output, index=False)
    manifest = [dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in files]
    (output.parent/'raw_source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return p

if __name__=='__main__':
    cli=argparse.ArgumentParser(); cli.add_argument('raw_dir'); cli.add_argument('--output',default='data/processed/np15_da_lmp_2025.csv')
    args=cli.parse_args(); prepare(args.raw_dir,args.output)
