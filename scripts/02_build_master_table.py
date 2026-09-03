"""
02_build_master_table.py
Joins the cleaned tables into a single trip-level analytical fact table
(one row per completed trip/load) plus a couple of supporting aggregates.
This master table is what most of the EDA/visualization in script 03 runs on.
"""
import pandas as pd
from pathlib import Path

CLEAN = Path(__file__).resolve().parent.parent / "data" / "cleaned"
OUT = Path(__file__).resolve().parent.parent / "data" / "cleaned"

loads = pd.read_csv(f"{CLEAN}/loads.csv", parse_dates=["load_date"])
trips = pd.read_csv(f"{CLEAN}/trips.csv", parse_dates=["dispatch_date"])
routes = pd.read_csv(f"{CLEAN}/routes.csv")
customers = pd.read_csv(f"{CLEAN}/customers.csv", parse_dates=["contract_start_date"])
drivers = pd.read_csv(f"{CLEAN}/drivers.csv", parse_dates=["hire_date", "termination_date", "date_of_birth"])
trucks = pd.read_csv(f"{CLEAN}/trucks.csv", parse_dates=["acquisition_date"])
fuel = pd.read_csv(f"{CLEAN}/fuel_purchases.csv", parse_dates=["purchase_date"])
delivery = pd.read_csv(f"{CLEAN}/delivery_events.csv",
                        parse_dates=["scheduled_datetime", "actual_datetime"])

# --- fuel aggregated to trip level (a trip can have multiple fuel stops) ---
fuel_agg = fuel.groupby("trip_id", as_index=False).agg(
    fuel_spend=("total_cost", "sum"),
    fuel_gallons_purchased=("gallons", "sum"),
    avg_price_per_gallon=("price_per_gallon", "mean"),
    n_fuel_stops=("fuel_purchase_id", "count"),
)

# --- delivery events aggregated to load level: on-time flag + detention ---
delivery_agg = delivery.groupby("load_id", as_index=False).agg(
    total_detention_minutes=("detention_minutes", "sum"),
    all_events_on_time=("on_time_flag", "all"),
    any_late=("on_time_flag", lambda s: (~s).any()),
)
# pull the delivery (not pickup) event's on-time flag as the primary service KPI
delivery_only = delivery[delivery["event_type"] == "Delivery"][
    ["load_id", "on_time_flag", "detention_minutes", "scheduled_datetime", "actual_datetime"]
].rename(columns={
    "on_time_flag": "delivery_on_time",
    "detention_minutes": "delivery_detention_minutes",
    "scheduled_datetime": "delivery_scheduled_dt",
    "actual_datetime": "delivery_actual_dt",
})

# --- master join: loads -> routes -> customers, then trips -> drivers -> trucks ---
master = loads.merge(routes, on="route_id", how="left", suffixes=("", "_route"))
master = master.merge(customers, on="customer_id", how="left", suffixes=("", "_cust"))
master = master.merge(trips, on="load_id", how="left", suffixes=("", "_trip"))
master = master.merge(drivers, on="driver_id", how="left", suffixes=("", "_drv"))
master = master.merge(trucks, on="truck_id", how="left", suffixes=("", "_trk"))
master = master.merge(fuel_agg, on="trip_id", how="left")
master = master.merge(delivery_only, on="load_id", how="left")

# derived KPIs
master["revenue_per_mile"] = master["revenue"] / master["actual_distance_miles"].replace(0, pd.NA)
master["total_cost_estimate"] = master["fuel_spend"].fillna(0)
master["margin_estimate"] = master["revenue"] - master["total_cost_estimate"]
master["load_month"] = master["load_date"].values.astype("datetime64[M]")
master["truck_age_years"] = ((master["load_date"] - master["acquisition_date"]).dt.days / 365.25)
master["driver_tenure_years"] = ((master["load_date"] - master["hire_date"]).dt.days / 365.25)

master.to_csv(f"{OUT}/master_trip_table.csv", index=False)
print(f"master_trip_table: {master.shape}")
print(master.dtypes)
print(f"\nNulls in key derived cols:\n{master[['revenue_per_mile','delivery_on_time','fuel_spend']].isna().sum()}")
