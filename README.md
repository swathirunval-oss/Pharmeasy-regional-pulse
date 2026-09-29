# Pharmeasy-regional-pulse
Pharmeasy Regional Order Pulse - Capstone Dashboard 
1. Project Overview
PharmEasy Regional Order Pulse is a data analytics capstone project designed to analyze regional order data and identify changes in order performance across Telangana, Andhra Pradesh, and Bengaluru.

2. Regions_master.csv - Master Data
This file contains master list of 10 regions. Only 3 columns: region, state, active

| Region | State | Note |
| Hyderabad | Telangana | Metro hub |
| Warangal | Telangana | Stable |
| Karimnagar | Telangana | Stable |
| Nizamabad | Telangana | Stable |
| Khammam | Telangana | Stable |
| Vijayawada | Andhra Pradesh | Stable |
| Visakhapatnam | Andhra Pradesh | Coastal |
| Guntur | Andhra Pradesh | Stable |
| Tirupati | Andhra Pradesh | Seasonal |
| Kurnool | Andhra Pradesh | Zero Order - COUNT(*)=1 but COUNT(order_id)=0 |

Key Finding
Kurnool: COUNT(*)=1 but COUNT(order_id)=0 - data anomaly, zero order case.

3. Tools
Python, Pandas, SQLite, SQL, GitHub, Dashboard

4. Workflow
Data Collection -> Cleaning -> SQLite -> SQL Analysis -> Visualization -> Reporting

5. Conclusion
End-to-end analytics with special handling for zero-order regions like Kurnool.
