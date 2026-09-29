"""End-to-end analytics pipeline for PharmEasy Regional Order Pulse."""
from pathlib import Path
from datetime import datetime, timezone
import json, sqlite3
import pandas as pd
ROOT=Path(__file__).resolve().parent; DATA=ROOT/'data'; OUT=ROOT/'outputs'; DB=DATA/'pharmeasy.db'
THRESHOLD=8.0
REQUIRED=['order_id','order_date','customer','region','product_category','quantity','sales','profit','discount']
def compute_percentage_change_v1(previous,current):
    """Percentage change; returns None when previous is zero or missing."""
    if previous is None or pd.isna(previous) or float(previous)==0:return None
    return round((float(current)-float(previous))/float(previous)*100,2)
def flag_significant_regions_v1(changes_dict,threshold=THRESHOLD):
    """Flag changes whose absolute percentage is strictly above threshold."""
    return {r:v for r,v in changes_dict.items() if v is not None and abs(float(v))>float(threshold)}
def save_state_v1(state,path=None):
    path=Path(path) if path else OUT/'state.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(state,indent=2),encoding='utf-8');return path
def load_previous_state_v1(path=None):
    path=Path(path) if path else OUT/'state.json'
    if not path.exists():return {}
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError,OSError):return {}
def clean_data(raw):
    missing=[c for c in REQUIRED if c not in raw.columns]
    if missing:raise ValueError(f'Missing required columns: {missing}')
    df=raw[REQUIRED].copy()
    for c in ['quantity','sales','profit','discount']:df[c]=pd.to_numeric(df[c],errors='coerce')
    df['order_date']=pd.to_datetime(df.order_date,errors='coerce')
    df=df.drop_duplicates('order_id',keep='first').dropna(subset=REQUIRED)
    df=df[(df.quantity>0)&(df.sales>=0)&df.discount.between(0,1)]
    df['order_date']=df.order_date.dt.strftime('%Y-%m-%d')
    return df.sort_values(['order_date','order_id']).reset_index(drop=True)
def run_pipeline():
    OUT.mkdir(exist_ok=True);raw=pd.read_csv(DATA/'raw_orders.csv');clean=clean_data(raw)
    if len(raw)!=2159 or len(clean)!=2100:raise ValueError(f'Expected 2159 raw / 2100 clean; got {len(raw)} / {len(clean)}')
    master=pd.read_csv(DATA/'regions_master.csv')
    with sqlite3.connect(DB) as conn:
        clean.to_sql('orders',conn,if_exists='replace',index=False);master.to_sql('regions_master',conn,if_exists='replace',index=False)
        monthly=pd.read_sql_query("SELECT region,strftime('%Y-%m',order_date) month,COUNT(DISTINCT order_id) orders,ROUND(SUM(sales),2) sales_inr,ROUND(SUM(profit),2) profit_inr FROM orders GROUP BY region,month ORDER BY region,month",conn)
        monthly.to_sql('monthly_region_metrics',conn,if_exists='replace',index=False)
        regional=pd.read_sql_query('SELECT r.region,COALESCE(COUNT(DISTINCT o.order_id),0) orders,COALESCE(ROUND(SUM(o.sales),2),0) sales_inr,COALESCE(ROUND(SUM(o.profit),2),0) profit_inr FROM regions_master r LEFT JOIN orders o ON r.region=o.region GROUP BY r.region ORDER BY r.region',conn)
        regional.to_sql('region_metrics',conn,if_exists='replace',index=False)
    monthly.to_csv(OUT/'monthly_region_metrics.csv',index=False);regional.to_csv(OUT/'region_metrics.csv',index=False);clean.to_csv(OUT/'orders_clean.csv',index=False)
    changes={}
    for region in master.region:
        g=monthly[monthly.region==region].set_index('month').sales_inr
        changes[region]=compute_percentage_change_v1(g['2026-04'],g['2026-05']) if '2026-04' in g and '2026-05' in g else None
    flagged=flag_significant_regions_v1(changes,THRESHOLD)
    risks=[{'region':r,'flag_type':'sales_change','change_pct':v,'threshold_pct':THRESHOLD,'review_status':'pending_human_review'} for r,v in flagged.items()]
    risks=pd.DataFrame(risks,columns=['region','flag_type','change_pct','threshold_pct','review_status']);risks.to_csv(OUT/'risk_flags.csv',index=False)
    top=regional.sort_values('sales_inr',ascending=False).iloc[0]
    (OUT/'cii_report.md').write_text(f"# CII Insight Report\n\n- **Context:** 2,100 cleaned synthetic orders from April–June 2026; total sales ₹{clean.sales.sum():,.2f}.\n- **Insight:** {top.region} has the highest total sales (₹{top.sales_inr:,.2f}); {len(risks)} review flags were raised.\n- **Implication:** Review significant regional movements before taking action.\n- **Caveat:** Synthetic data, not actual PharmEasy records. Kurnool is retained with zero orders.\n",encoding='utf-8')
    memo=f"# Regional Pulse — Decision Memo\n\n1. **Context:** April–June 2026 synthetic sample; 2,100 valid orders.\n2. **Key insight:** {top.region} leads total sales at ₹{top.sales_inr:,.2f}.\n3. **Business implication:** Regional totals and monthly changes identify areas for investigation.\n4. **Recommendation:** Review flags and validate drivers with operational teams.\n5. **Risk / limitation:** Synthetic data; flags are not causal explanations or automatic decisions.\n6. **Owner:** Regional Operations with Analytics support.\n7. **Next check:** Validate source data, compare the next month, and document flag outcomes.\n"
    (OUT/'business_memo.md').write_text(memo,encoding='utf-8')
    state={'period':'2026-04_to_2026-06','clean_rows':len(clean),'changes_apr_may_pct':changes,'flagged_regions':list(flagged)};save_state_v1(state)
    now=datetime.now(timezone.utc).isoformat();audit=[{'event':'data_validation','timestamp_utc':now,'raw_rows':len(raw),'clean_rows':len(clean),'status':'passed'},{'event':'metrics_and_flags','timestamp_utc':now,'regions':len(master),'flag_count':len(risks),'status':'completed'},{'event':'report_generation','timestamp_utc':now,'reports':['cii_report.md','business_memo.md'],'approval_status':'pending_human_review'}]
    (OUT/'audit_log.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(f'Pipeline complete: {len(raw)} raw -> {len(clean)} clean; {len(master)} regions; {len(risks)} flags.')
if __name__=='__main__':run_pipeline()
