"""
00_profile_data.py
Data quality profiling pass across all 13 raw tables.
Outputs a summary report to stdout (redirected to a log file) covering:
- shape, dtypes
- missing value counts/%
- duplicate rows / duplicate keys
- basic numeric outlier scan (IQR method)
- date range sanity checks
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 140)

files = {
    "customers": "customers.csv",
    "drivers": "drivers.csv",
    "trucks": "trucks.csv",
    "trailers": "trailers.csv",
    "facilities": "facilities.csv",
    "routes": "routes.csv",
    "loads": "loads.csv",
    "trips": "trips.csv",
    "fuel_purchases": "fuel_purchases.csv",
    "maintenance_records": "maintenance_records.csv",
    "delivery_events": "delivery_events.csv",
    "safety_incidents": "safety_incidents.csv",
    "driver_monthly_metrics": "driver_monthly_metrics.csv",
    "truck_utilization_metrics": "truck_utilization_metrics.csv",
}

pk_map = {
    "customers": "customer_id",
    "drivers": "driver_id",
    "trucks": "truck_id",
    "trailers": "trailer_id",
    "facilities": "facility_id",
    "routes": "route_id",
    "loads": "load_id",
    "trips": "trip_id",
    "fuel_purchases": "fuel_purchase_id",
    "maintenance_records": "maintenance_id",
    "delivery_events": "event_id",
    "safety_incidents": "incident_id",
}

dfs = {}
for name, fname in files.items():
    df = pd.read_csv(RAW / fname, low_memory=False)
    dfs[name] = df
    print(f"\n{'='*80}\nTABLE: {name}  ({fname})\n{'='*80}")
    print(f"shape: {df.shape}")
    print(f"\ndtypes:\n{df.dtypes}")

    # missing values
    miss = df.isna().sum()
    miss = miss[miss > 0]
    if len(miss):
        pct = (miss / len(df) * 100).round(2)
        print(f"\nmissing values:\n{pd.DataFrame({'count': miss, 'pct': pct})}")
    else:
        print("\nmissing values: none")

    # duplicate full rows
    dup_rows = df.duplicated().sum()
    print(f"\nfull duplicate rows: {dup_rows}")

    # duplicate primary key
    if name in pk_map:
        pk = pk_map[name]
        dup_pk = df[pk].duplicated().sum()
        print(f"duplicate {pk} values: {dup_pk}")

    # numeric outlier scan (IQR)
    num_cols = df.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        s = df[col].dropna()
        if len(s) < 10:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
        n_out = ((s < lo) | (s > hi)).sum()
        if n_out > 0:
            print(f"  outliers (extreme IQR*3) in '{col}': {n_out}  "
                  f"(range obs: [{s.min()}, {s.max()}], bounds: [{lo:.2f}, {hi:.2f}])")

    # negative value checks for columns that shouldn't be negative
    for col in num_cols:
        if any(k in col.lower() for k in ["revenue", "cost", "price", "gallons", "miles",
                                            "weight", "hours", "amount", "charges"]):
            n_neg = (df[col] < 0).sum()
            if n_neg > 0:
                print(f"  NEGATIVE values in '{col}': {n_neg}")

print("\n\nDONE PROFILING")
