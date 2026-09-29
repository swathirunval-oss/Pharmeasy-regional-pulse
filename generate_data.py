from pathlib import Path
import pandas as pd
p=Path(__file__).parent/'data'/'raw_orders.csv'
if not p.exists():raise FileNotFoundError(f'Missing included dataset: {p}')
df=pd.read_csv(p);print(f'Raw dataset ready: {len(df)} rows; {df.order_id.nunique()} unique IDs')
