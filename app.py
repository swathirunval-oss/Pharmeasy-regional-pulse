from pathlib import Path
import sqlite3,pandas as pd,plotly.express as px,streamlit as st
ROOT=Path(__file__).resolve().parent;DB=ROOT/'data'/'pharmeasy.db';OUT=ROOT/'outputs'
st.set_page_config(page_title='PharmEasy Regional Pulse',page_icon='📊',layout='wide')
st.title('PharmEasy Regional Order Pulse');st.caption('Capstone dashboard • Synthetic demonstration data only')
if not DB.exists():st.warning('Run `python run_all.py` first.');st.stop()
with sqlite3.connect(DB) as conn:
 orders=pd.read_sql_query('SELECT * FROM orders',conn,parse_dates=['order_date']);regions=pd.read_sql_query('SELECT * FROM region_metrics',conn);monthly=pd.read_sql_query('SELECT * FROM monthly_region_metrics',conn)
choice=st.sidebar.multiselect('Filter regions',regions.region.tolist(),default=regions.region.tolist());f=orders[orders.region.isin(choice)];r=regions[regions.region.isin(choice)];m=monthly[monthly.region.isin(choice)]
a,b,c=st.columns(3);a.metric('Clean orders',f.order_id.nunique());b.metric('Sales (₹)',f.sales.sum());c.metric('Profit (₹)',f.profit.sum())
st.header('Level 1 — Overview');x,y=st.columns(2);x.plotly_chart(px.bar(r,x='region',y='sales_inr',title='Sales by region'),use_container_width=True);y.plotly_chart(px.bar(r,x='region',y='profit_inr',title='Profit by region'),use_container_width=True)
st.header('Level 2 — Breakdown');x,y=st.columns(2);x.plotly_chart(px.line(m,x='month',y='sales_inr',color='region',markers=True,title='Monthly sales trend'),use_container_width=True);y.plotly_chart(px.bar(f.groupby('product_category',as_index=False).sales.sum(),x='product_category',y='sales',title='Sales by category'),use_container_width=True)
st.header('Level 3 — Detail');st.dataframe(r,use_container_width=True,hide_index=True)
if (OUT/'risk_flags.csv').exists():st.dataframe(pd.read_csv(OUT/'risk_flags.csv').query('region in @choice'),use_container_width=True,hide_index=True)
st.header('Storyline & Q&A');st.markdown('**Overview:** Compare regional sales and profit. **Breakdown:** Explore monthly and category patterns. **Action signal:** Review flagged changes; a flag is not proof of cause.')
with st.expander('Why is Kurnool shown with zero orders?'):st.write('It is present in the region master but has no supplied order rows; no sales are imputed.')
with st.expander('What does an 8% flag mean?'):st.write('Absolute April-to-May sales change strictly greater than 8%.')
with st.expander('Is this actual PharmEasy data?'):st.write('No. This is synthetic demonstration data.')
