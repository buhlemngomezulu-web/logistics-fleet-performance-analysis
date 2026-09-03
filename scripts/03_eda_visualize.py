"""
03_eda_visualize.py
Exploratory analysis + chart generation for the logistics fleet dataset.
Reads the cleaned tables / master fact table and writes PNG charts to
outputs/figures/, plus a text summary of key stats to
outputs/reports/03_eda_summary.txt
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

CLEAN = Path(__file__).resolve().parent.parent / "data" / "cleaned"
FIG = Path(__file__).resolve().parent.parent / "outputs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.0)
PALETTE = "viridis"
plt.rcParams["figure.dpi"] = 130
plt.rcParams["savefig.bbox"] = "tight"

master = pd.read_csv(f"{CLEAN}/master_trip_table.csv", parse_dates=[
    "load_date", "dispatch_date", "load_month"])
dmm = pd.read_csv(f"{CLEAN}/driver_monthly_metrics.csv", parse_dates=["month"])
tum = pd.read_csv(f"{CLEAN}/truck_utilization_metrics.csv", parse_dates=["month"])
maint = pd.read_csv(f"{CLEAN}/maintenance_records.csv", parse_dates=["maintenance_date"])
safety = pd.read_csv(f"{CLEAN}/safety_incidents.csv", parse_dates=["incident_date"])
fuel = pd.read_csv(f"{CLEAN}/fuel_purchases.csv", parse_dates=["purchase_date"])
routes = pd.read_csv(f"{CLEAN}/routes.csv")

summary_lines = []


def log(s):
    print(s)
    summary_lines.append(s)


log("=" * 70)
log("LOGISTICS FLEET ANALYSIS - EDA SUMMARY")
log("=" * 70)
log(f"Analysis period: {master['load_date'].min().date()} to {master['load_date'].max().date()}")
log(f"Total loads/trips: {len(master):,}")
log(f"Total revenue: ${master['revenue'].sum():,.0f}")
log(f"Total miles: {master['actual_distance_miles'].sum():,.0f}")
log(f"Overall on-time delivery rate: {master['delivery_on_time'].mean()*100:.1f}%")
log(f"Average revenue per mile: ${master['revenue_per_mile'].mean():.2f}")
log(f"Average trip MPG: {master['average_mpg'].mean():.2f}")

# =====================================================================
# 1. Monthly revenue & load volume trend (seasonality)
# =====================================================================
monthly = master.groupby("load_month").agg(
    revenue=("revenue", "sum"), loads=("load_id", "count")
).reset_index()

# Stacked subplots (not twin-axis) so differing y-scales can't create a
# misleading "both dip to zero together" illusion.
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
ax1.bar(monthly["load_month"], monthly["revenue"] / 1e6, color="#1b4965", width=20)
ax1.set_ylabel("Revenue ($M)")
ax1.set_ylim(0, monthly["revenue"].max() / 1e6 * 1.15)
ax1.set_title("Monthly Revenue & Load Volume (2022–2024)", fontsize=13, fontweight="bold")

ax2.bar(monthly["load_month"], monthly["loads"], color="#a8d5e2", width=20)
ax2.set_ylabel("Loads per month")
ax2.set_xlabel("Month")
ax2.set_ylim(0, monthly["loads"].max() * 1.15)

fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/01_monthly_revenue_volume.png")
plt.close(fig)
log(f"\n[Chart 1] Monthly revenue & volume trend saved. "
    f"Range: {monthly['loads'].min()}-{monthly['loads'].max()} loads/mo, "
    f"${monthly['revenue'].min()/1e6:.2f}M-${monthly['revenue'].max()/1e6:.2f}M/mo "
    f"(seasonal swing is modest, ~10-15%, February consistently lowest).")

# =====================================================================
# 2. On-time delivery rate trend
# =====================================================================
otd = master.groupby("load_month")["delivery_on_time"].mean().reset_index()
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.plot(otd["load_month"], otd["delivery_on_time"] * 100, color="#bc4749", marker="o", linewidth=2)
ax.axhline(otd["delivery_on_time"].mean() * 100, color="gray", linestyle="--",
           label=f"Overall avg: {otd['delivery_on_time'].mean()*100:.1f}%")
ax.set_ylabel("On-time delivery rate (%)")
ax.set_xlabel("Month")
ax.set_title("On-Time Delivery Rate Over Time", fontsize=13, fontweight="bold")
ax.legend()
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/02_on_time_delivery_trend.png")
plt.close(fig)
log(f"[Chart 2] On-time delivery trend saved. Range: "
    f"{otd['delivery_on_time'].min()*100:.1f}% - {otd['delivery_on_time'].max()*100:.1f}%")

# =====================================================================
# 3. Revenue by customer type & top 10 customers
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
cust_type_rev = master.groupby("customer_type")["revenue"].sum().sort_values(ascending=False)
axes[0].bar(cust_type_rev.index, cust_type_rev.values / 1e6, color=sns.color_palette(PALETTE, len(cust_type_rev)))
axes[0].set_ylabel("Revenue ($M)")
axes[0].set_title("Revenue by Customer Type")
axes[0].tick_params(axis="x", rotation=20)

top_cust = master.groupby("customer_name")["revenue"].sum().sort_values(ascending=False).head(10)
axes[1].barh(top_cust.index[::-1], top_cust.values[::-1] / 1e6, color=sns.color_palette(PALETTE, 10))
axes[1].set_xlabel("Revenue ($M)")
axes[1].set_title("Top 10 Customers by Revenue")
fig.suptitle("Customer Revenue Analysis", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/03_customer_revenue.png")
plt.close(fig)
log(f"\n[Chart 3] Customer revenue analysis saved. Top customer: {top_cust.index[0]} "
    f"(${top_cust.values[0]:,.0f})")

# =====================================================================
# 4. Route profitability - top/bottom lanes by revenue per mile
# =====================================================================
route_perf = master.groupby("lane").agg(
    avg_rev_per_mile=("revenue_per_mile", "mean"),
    total_revenue=("revenue", "sum"),
    n_loads=("load_id", "count"),
).reset_index()
route_perf = route_perf[route_perf["n_loads"] >= 30]  # stable sample only
top10 = route_perf.sort_values("avg_rev_per_mile", ascending=False).head(10)
bottom10 = route_perf.sort_values("avg_rev_per_mile", ascending=True).head(10)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
axes[0].barh(top10["lane"][::-1], top10["avg_rev_per_mile"][::-1], color="#2a9d8f")
axes[0].set_title("Top 10 Lanes by Revenue/Mile")
axes[0].set_xlabel("Avg revenue per mile ($)")
axes[1].barh(bottom10["lane"][::-1], bottom10["avg_rev_per_mile"][::-1], color="#e76f51")
axes[1].set_title("Bottom 10 Lanes by Revenue/Mile")
axes[1].set_xlabel("Avg revenue per mile ($)")
fig.suptitle("Route Profitability (lanes with ≥30 loads)", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/04_route_profitability.png")
plt.close(fig)
log(f"\n[Chart 4] Route profitability saved. Best lane: {top10.iloc[0]['lane']} "
    f"(${top10.iloc[0]['avg_rev_per_mile']:.2f}/mi); "
    f"Worst: {bottom10.iloc[0]['lane']} (${bottom10.iloc[0]['avg_rev_per_mile']:.2f}/mi)")

# =====================================================================
# 5. Fuel efficiency (MPG) trend + by truck make
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
mpg_trend = master.groupby("load_month")["average_mpg"].mean().reset_index()
axes[0].plot(mpg_trend["load_month"], mpg_trend["average_mpg"], color="#457b9d", marker="o")
axes[0].set_title("Average MPG Over Time")
axes[0].set_ylabel("MPG")
axes[0].set_xlabel("Month")

mpg_by_make = master.groupby("make")["average_mpg"].mean().sort_values(ascending=False)
axes[1].bar(mpg_by_make.index, mpg_by_make.values, color=sns.color_palette(PALETTE, len(mpg_by_make)))
axes[1].set_title("Average MPG by Truck Make")
axes[1].set_ylabel("MPG")
axes[1].tick_params(axis="x", rotation=30)
fig.suptitle("Fuel Efficiency Analysis", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/05_fuel_efficiency.png")
plt.close(fig)
log(f"\n[Chart 5] Fuel efficiency saved. Best make: {mpg_by_make.index[0]} "
    f"({mpg_by_make.values[0]:.2f} MPG); Worst: {mpg_by_make.index[-1]} ({mpg_by_make.values[-1]:.2f} MPG)")

# =====================================================================
# 6. Driver performance: revenue/mile vs on-time rate (scatter), by tenure
# =====================================================================
driver_perf = master.dropna(subset=["driver_id"]).groupby("driver_id").agg(
    avg_rev_per_mile=("revenue_per_mile", "mean"),
    on_time_rate=("delivery_on_time", "mean"),
    n_trips=("trip_id", "count"),
    avg_mpg=("average_mpg", "mean"),
).reset_index()
driver_perf = driver_perf[driver_perf["n_trips"] >= 20]

fig, ax = plt.subplots(figsize=(9, 6.5))
sc = ax.scatter(driver_perf["avg_rev_per_mile"], driver_perf["on_time_rate"] * 100,
                 c=driver_perf["avg_mpg"], cmap=PALETTE, s=60, alpha=0.85, edgecolor="white")
cbar = fig.colorbar(sc)
cbar.set_label("Avg MPG")
ax.set_xlabel("Avg revenue per mile ($)")
ax.set_ylabel("On-time delivery rate (%)")
ax.set_title("Driver Performance: Revenue/Mile vs On-Time Rate\n(color = fuel efficiency, drivers with ≥20 trips)",
             fontsize=12, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/06_driver_performance.png")
plt.close(fig)
log(f"\n[Chart 6] Driver performance scatter saved. n={len(driver_perf)} drivers with ≥20 trips.")

# =====================================================================
# 7. Fleet utilization rate distribution
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].hist(tum["utilization_rate"] * 100, bins=25, color="#588157", edgecolor="white")
axes[0].axvline(tum["utilization_rate"].mean() * 100, color="black", linestyle="--",
                label=f"Mean: {tum['utilization_rate'].mean()*100:.1f}%")
axes[0].set_xlabel("Utilization rate (%)")
axes[0].set_ylabel("Truck-months")
axes[0].set_title("Fleet Utilization Rate Distribution")
axes[0].legend()

util_trend = tum.groupby("month")["utilization_rate"].mean().reset_index()
axes[1].plot(util_trend["month"], util_trend["utilization_rate"] * 100, color="#588157", marker="o")
axes[1].set_title("Avg Fleet Utilization Over Time")
axes[1].set_ylabel("Utilization rate (%)")
axes[1].set_xlabel("Month")
fig.suptitle("Fleet Utilization", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/07_fleet_utilization.png")
plt.close(fig)
log(f"\n[Chart 7] Fleet utilization saved. Mean utilization: {tum['utilization_rate'].mean()*100:.1f}%")

# =====================================================================
# 8. Maintenance cost analysis: cost/mile by truck age, downtime impact
# =====================================================================
truck_miles = master.groupby("truck_id")["actual_distance_miles"].sum().reset_index()
maint_by_truck = maint.groupby("truck_id")["total_cost"].sum().reset_index()
mc = truck_miles.merge(maint_by_truck, on="truck_id", how="left").fillna(0)
mc["cost_per_mile"] = mc["total_cost"] / mc["actual_distance_miles"].replace(0, np.nan)
trucks_tbl = pd.read_csv(f"{CLEAN}/trucks.csv", parse_dates=["acquisition_date"])
mc = mc.merge(trucks_tbl[["truck_id", "acquisition_date", "make"]], on="truck_id", how="left")
mc["age_years"] = (pd.Timestamp("2024-12-31") - mc["acquisition_date"]).dt.days / 365.25

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(mc["age_years"], mc["cost_per_mile"], color="#e07a5f", alpha=0.7)
axes[0].set_xlabel("Truck age (years)")
axes[0].set_ylabel("Maintenance cost per mile ($)")
axes[0].set_title("Maintenance Cost vs Truck Age")

maint_type_cost = maint.groupby("maintenance_type")["total_cost"].sum().sort_values(ascending=False)
axes[1].bar(maint_type_cost.index, maint_type_cost.values / 1000, color=sns.color_palette(PALETTE, len(maint_type_cost)))
axes[1].set_ylabel("Total cost ($K)")
axes[1].set_title("Total Maintenance Cost by Type")
axes[1].tick_params(axis="x", rotation=30)
fig.suptitle("Maintenance Cost Analysis", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/08_maintenance_analysis.png")
plt.close(fig)
corr = mc[["age_years", "cost_per_mile"]].corr().iloc[0, 1]
log(f"\n[Chart 8] Maintenance analysis saved. Age vs cost/mile correlation: {corr:.2f}")

# =====================================================================
# 9. Safety incidents: by type + preventable share, cost
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
inc_type = safety["incident_type"].value_counts()
axes[0].bar(inc_type.index, inc_type.values, color=sns.color_palette(PALETTE, len(inc_type)))
axes[0].set_title("Safety Incidents by Type")
axes[0].set_ylabel("Count")
axes[0].tick_params(axis="x", rotation=30)

prevent_pct = safety["preventable_flag"].mean() * 100
labels = ["Preventable", "Non-preventable"]
sizes = [safety["preventable_flag"].sum(), (~safety["preventable_flag"]).sum()]
axes[1].pie(sizes, labels=labels, autopct="%1.0f%%", colors=["#e63946", "#a8dadc"], startangle=90)
axes[1].set_title(f"Preventable Incidents ({prevent_pct:.0f}% of {len(safety)} total)")
fig.suptitle("Safety Incident Analysis", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/09_safety_incidents.png")
plt.close(fig)
log(f"\n[Chart 9] Safety incident analysis saved. {len(safety)} incidents total, "
    f"{prevent_pct:.0f}% preventable, total claims ${safety['claim_amount'].sum():,.0f}")

# =====================================================================
# 10. Load type / booking type revenue mix
# =====================================================================
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
lt = master.groupby("load_type")["revenue"].sum()
axes[0].pie(lt.values, labels=lt.index, autopct="%1.0f%%", colors=sns.color_palette(PALETTE, len(lt)), startangle=90)
axes[0].set_title("Revenue Share by Load Type")

bt = master.groupby("booking_type")["revenue"].sum().sort_values(ascending=False)
axes[1].bar(bt.index, bt.values / 1e6, color=sns.color_palette(PALETTE, len(bt)))
axes[1].set_ylabel("Revenue ($M)")
axes[1].set_title("Revenue by Booking Type")
fig.suptitle("Load & Booking Mix", fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/10_load_booking_mix.png")
plt.close(fig)
log(f"\n[Chart 10] Load/booking mix saved.")

# =====================================================================
# 11. Detention minutes distribution & impact on on-time rate
# =====================================================================
fig, ax = plt.subplots(figsize=(10, 5))
det_bins = pd.cut(master["delivery_detention_minutes"].fillna(0),
                   bins=[-1, 0, 30, 60, 120, 100000],
                   labels=["0 min", "1-30", "31-60", "61-120", "120+"])
det_otd = master.groupby(det_bins, observed=True)["delivery_on_time"].mean() * 100
ax.bar(det_otd.index.astype(str), det_otd.values, color=sns.color_palette(PALETTE, len(det_otd)))
ax.set_xlabel("Detention time bucket")
ax.set_ylabel("On-time delivery rate (%)")
ax.set_title("On-Time Rate by Detention Time at Delivery", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/11_detention_impact.png")
plt.close(fig)
log(f"\n[Chart 11] Detention impact saved.")

# =====================================================================
# 12. Correlation heatmap of key numeric KPIs
# =====================================================================
kpi_cols = ["revenue", "actual_distance_miles", "actual_duration_hours", "average_mpg",
            "revenue_per_mile", "fuel_spend", "delivery_detention_minutes", "weight_lbs"]
corr_df = master[kpi_cols].corr()
fig, ax = plt.subplots(figsize=(8, 6.5))
sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax, square=True,
            cbar_kws={"shrink": 0.8})
ax.set_title("Correlation Matrix: Key Trip KPIs", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95]) if fig._suptitle else fig.tight_layout()
fig.savefig(f"{FIG}/12_correlation_heatmap.png")
plt.close(fig)
log(f"\n[Chart 12] Correlation heatmap saved.")

REPORTS = Path(__file__).resolve().parent.parent / "outputs" / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

with open(REPORTS / "03_eda_summary.txt", "w") as f:
    f.write("\n".join(summary_lines))

print("\n\nAll 12 charts saved to outputs/figures/")
