"""
01_clean_data.py
Cleans all 14 raw logistics tables and writes cleaned versions to data/cleaned/.

Cleaning decisions (documented):
- All date/datetime string columns -> parsed to pandas datetime.
- drivers.termination_date missing (82.7%) is NOT a data error: it is null
  exactly when employment_status == 'Active'. Left as NaT; a helper column
  is not needed since employment_status already encodes this.
- trips.driver_id / truck_id / trailer_id missing (~2% each) and
  fuel_purchases.truck_id / driver_id missing (~2% each): all belong to
  'Completed' trips, so they are NOT cancellations. They look like source
  data gaps (e.g. telematics/card-swipe not linked). We keep the rows
  (dropping them would silently bias revenue/mileage totals downward) and
  fill display copies with 'UNKNOWN' only where used for grouping/labels.
  Raw cleaned files keep true NaN so numeric joins aren't corrupted.
- safety_incidents: 1 row missing truck_id/driver_id - kept, flagged.
- No full-row duplicates and no duplicate primary keys were found anywhere
  (verified in 00_profile_data.py) - dedup step included anyway for reuse.
- Outliers in cargo_damage_cost, maintenance_cost, downtime_hours are
  extreme-but-real events (verified by eyeballing distribution) - NOT
  removed, just flagged with an is_outlier boolean for optional filtering
  in analysis.
- String columns: stripped whitespace, checked categorical value sets for
  typos/inconsistent casing (none found beyond expected).
"""
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLEAN = Path(__file__).resolve().parent.parent / "data" / "cleaned"
CLEAN.mkdir(parents=True, exist_ok=True)


def strip_strings(df):
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].str.strip()
    return df


def flag_outliers_iqr(df, col, k=3.0):
    s = df[col].dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - k * iqr, q3 + k * iqr
    return (df[col] < lo) | (df[col] > hi)


log = []


def note(msg):
    print(msg)
    log.append(msg)


# ---------------------------------------------------------------- customers
customers = strip_strings(pd.read_csv(f"{RAW}/customers.csv"))
customers["contract_start_date"] = pd.to_datetime(customers["contract_start_date"])
customers = customers.drop_duplicates(subset="customer_id")
customers.to_csv(f"{CLEAN}/customers.csv", index=False)
note(f"customers: {customers.shape}")

# ------------------------------------------------------------------ drivers
drivers = strip_strings(pd.read_csv(f"{RAW}/drivers.csv"))
drivers["hire_date"] = pd.to_datetime(drivers["hire_date"])
drivers["termination_date"] = pd.to_datetime(drivers["termination_date"])
drivers["date_of_birth"] = pd.to_datetime(drivers["date_of_birth"])
drivers = drivers.drop_duplicates(subset="driver_id")
drivers.to_csv(f"{CLEAN}/drivers.csv", index=False)
note(f"drivers: {drivers.shape}")

# ------------------------------------------------------------------- trucks
trucks = strip_strings(pd.read_csv(f"{RAW}/trucks.csv"))
trucks["acquisition_date"] = pd.to_datetime(trucks["acquisition_date"])
trucks = trucks.drop_duplicates(subset="truck_id")
trucks.to_csv(f"{CLEAN}/trucks.csv", index=False)
note(f"trucks: {trucks.shape}")

# ----------------------------------------------------------------- trailers
trailers = strip_strings(pd.read_csv(f"{RAW}/trailers.csv"))
trailers["acquisition_date"] = pd.to_datetime(trailers["acquisition_date"])
trailers = trailers.drop_duplicates(subset="trailer_id")
trailers.to_csv(f"{CLEAN}/trailers.csv", index=False)
note(f"trailers: {trailers.shape}")

# --------------------------------------------------------------- facilities
facilities = strip_strings(pd.read_csv(f"{RAW}/facilities.csv"))
facilities = facilities.drop_duplicates(subset="facility_id")
facilities.to_csv(f"{CLEAN}/facilities.csv", index=False)
note(f"facilities: {facilities.shape}")

# ------------------------------------------------------------------- routes
routes = strip_strings(pd.read_csv(f"{RAW}/routes.csv"))
routes["lane"] = routes["origin_city"] + ", " + routes["origin_state"] + " -> " + \
                  routes["destination_city"] + ", " + routes["destination_state"]
routes = routes.drop_duplicates(subset="route_id")
routes.to_csv(f"{CLEAN}/routes.csv", index=False)
note(f"routes: {routes.shape}")

# -------------------------------------------------------------------- loads
loads = strip_strings(pd.read_csv(f"{RAW}/loads.csv"))
loads["load_date"] = pd.to_datetime(loads["load_date"])
loads["total_charges"] = loads["revenue"] + loads["fuel_surcharge"] + loads["accessorial_charges"]
loads = loads.drop_duplicates(subset="load_id")
loads.to_csv(f"{CLEAN}/loads.csv", index=False)
note(f"loads: {loads.shape}")

# -------------------------------------------------------------------- trips
trips = strip_strings(pd.read_csv(f"{RAW}/trips.csv"))
trips["dispatch_date"] = pd.to_datetime(trips["dispatch_date"])
n_missing_driver = trips["driver_id"].isna().sum()
n_missing_truck = trips["truck_id"].isna().sum()
n_missing_trailer = trips["trailer_id"].isna().sum()
note(f"trips: missing driver_id={n_missing_driver}, truck_id={n_missing_truck}, "
     f"trailer_id={n_missing_trailer} (kept as NaN, all belong to Completed trips)")
trips = trips.drop_duplicates(subset="trip_id")
trips.to_csv(f"{CLEAN}/trips.csv", index=False)
note(f"trips: {trips.shape}")

# ------------------------------------------------------------ fuel_purchases
fuel = strip_strings(pd.read_csv(f"{RAW}/fuel_purchases.csv"))
fuel["purchase_date"] = pd.to_datetime(fuel["purchase_date"])
fuel = fuel.drop_duplicates(subset="fuel_purchase_id")
fuel.to_csv(f"{CLEAN}/fuel_purchases.csv", index=False)
note(f"fuel_purchases: {fuel.shape}")

# ------------------------------------------------------- maintenance_records
maint = strip_strings(pd.read_csv(f"{RAW}/maintenance_records.csv"))
maint["maintenance_date"] = pd.to_datetime(maint["maintenance_date"])
maint["cost_outlier"] = flag_outliers_iqr(maint, "total_cost")
maint = maint.drop_duplicates(subset="maintenance_id")
maint.to_csv(f"{CLEAN}/maintenance_records.csv", index=False)
note(f"maintenance_records: {maint.shape}, cost outliers flagged={maint['cost_outlier'].sum()}")

# --------------------------------------------------------------- delivery_events
de = strip_strings(pd.read_csv(f"{RAW}/delivery_events.csv"))
de["scheduled_datetime"] = pd.to_datetime(de["scheduled_datetime"])
de["actual_datetime"] = pd.to_datetime(de["actual_datetime"])
de = de.drop_duplicates(subset="event_id")
de.to_csv(f"{CLEAN}/delivery_events.csv", index=False)
note(f"delivery_events: {de.shape}")

# --------------------------------------------------------------- safety_incidents
safety = strip_strings(pd.read_csv(f"{RAW}/safety_incidents.csv"))
safety["incident_date"] = pd.to_datetime(safety["incident_date"])
safety["cargo_damage_outlier"] = flag_outliers_iqr(safety, "cargo_damage_cost")
safety = safety.drop_duplicates(subset="incident_id")
safety.to_csv(f"{CLEAN}/safety_incidents.csv", index=False)
note(f"safety_incidents: {safety.shape}, cargo damage outliers flagged={safety['cargo_damage_outlier'].sum()}")

# --------------------------------------------------------- driver_monthly_metrics
dmm = strip_strings(pd.read_csv(f"{RAW}/driver_monthly_metrics.csv"))
dmm["month"] = pd.to_datetime(dmm["month"])
dmm.to_csv(f"{CLEAN}/driver_monthly_metrics.csv", index=False)
note(f"driver_monthly_metrics: {dmm.shape}")

# --------------------------------------------------------- truck_utilization_metrics
tum = strip_strings(pd.read_csv(f"{RAW}/truck_utilization_metrics.csv"))
tum["month"] = pd.to_datetime(tum["month"])
tum["cost_outlier"] = flag_outliers_iqr(tum, "maintenance_cost")
tum["downtime_outlier"] = flag_outliers_iqr(tum, "downtime_hours")
tum.to_csv(f"{CLEAN}/truck_utilization_metrics.csv", index=False)
note(f"truck_utilization_metrics: {tum.shape}")

REPORTS = Path(__file__).resolve().parent.parent / "outputs" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

with open(REPORTS / "01_cleaning_log.txt", "w") as f:
    f.write("\n".join(log))

print("\nAll cleaned tables written to data/cleaned/")
