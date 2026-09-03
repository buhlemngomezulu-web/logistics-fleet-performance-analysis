# Logistics Fleet Performance Analysis

An end-to-end data analysis of a trucking and logistics fleet covering **January 2022 to December 2024**. The project examines revenue, delivery performance, fleet utilization, fuel efficiency, maintenance, safety, customer mix, and route profitability to identify operational trends and potential improvement areas.

## Business Question

**How can a logistics company improve delivery performance and operational efficiency while maintaining fleet utilization and controlling costs?**

## Project Overview

The analysis uses **14 relational tables** covering:

- Customers
- Drivers
- Trucks
- Trailers
- Facilities
- Routes
- Loads
- Trips
- Fuel purchases
- Maintenance records
- Delivery events
- Safety incidents
- Driver monthly metrics
- Truck utilization metrics

The dataset contains:

- **85,410** completed loads/trips
- **$262.5M** total revenue
- **122.2M** miles driven
- **150** drivers
- **120** trucks
- **180** trailers
- **200** customers
- **50** facilities
- **58** routes

## Analysis Pipeline

The project follows a reproducible workflow:

```text
Raw Data
   ↓
Data Profiling
   ↓
Data Cleaning
   ↓
Master Trip-Level Table
   ↓
Exploratory Data Analysis
   ↓
Business Insights & Recommendations
   ↓
Final Report
```

### 1. Data Profiling

`scripts/00_profile_data.py`

Profiles all 14 source tables for:

- Missing values
- Data types
- Duplicate records
- Primary-key issues
- Outliers
- Referential integrity

### 2. Data Cleaning

`scripts/01_clean_data.py`

Applies documented cleaning decisions, including:

- Datetime conversion
- Missing-value handling
- Duplicate checks
- Outlier identification
- Data-quality validation

Original raw CSV files remain untouched.

### 3. Master Table Construction

`scripts/02_build_master_table.py`

Joins the cleaned relational tables into a trip-level analytical fact table containing operational, financial, delivery, fuel, route, driver, and vehicle metrics.

### 4. Exploratory Data Analysis

`scripts/03_eda_visualize.py`

Produces 12 visualizations covering:

- Revenue and load volume trends
- On-time delivery performance
- Customer revenue
- Route profitability
- Fuel efficiency
- Driver performance
- Fleet utilization
- Maintenance costs
- Safety incidents
- Load and booking mix
- Detention-time impact
- KPI correlations

### 5. Report Generation

`scripts/build_report.js`

Uses `docx` to compile the analysis findings and visualizations into a professional Word report.

## Key Findings

### Delivery Performance

Only 44.6% of deliveries were on time. Performance remained relatively flat throughout the three-year period.

The shortfall was broadly consistent across drivers, routes, facilities, load types, booking types, and detention-time buckets. This suggests that delivery scheduling and target-setting should be investigated as a potential systemic issue, rather than assuming the problem is concentrated among individual drivers or facilities.

### Revenue & Volume

Revenue and load volume remained relatively stable throughout 2022–2024, with a recurring seasonal decline during February.

- Total revenue: $262.5M
- Completed loads/trips: 85,410
- Total distance: 122.2M miles

### Fleet Utilization

Average fleet utilization was 83%.

Only 1.2% of truck-month observations fell below 50% utilization, indicating relatively strong utilization across the fleet.

### Fuel Efficiency

Fuel efficiency remained highly consistent across the analysis period and across truck manufacturers.

Average MPG ranged approximately from 6.45 to 6.57, suggesting limited opportunity for improvement through truck-make selection alone.

### Maintenance

Maintenance cost per mile showed a weak relationship with truck age (correlation = -0.11).

This suggests that maintenance costs were not strongly increasing with vehicle age within the observed fleet.

### Safety

The dataset contained 170 safety incidents, of which approximately 38% were classified as preventable.

Total safety claims amounted to approximately $2.65M, representing about 1% of total revenue.

### Route Profitability

Revenue per mile varied substantially between established routes, ranging from approximately $1.48 to $2.72 per mile.

This indicates that route-level pricing and capacity allocation may provide a meaningful opportunity for further analysis.

## Recommendations

1. Investigate delivery scheduling assumptions by comparing scheduled delivery windows with typical transit times and actual delivery durations.
2. Use route-level revenue-per-mile analysis to support pricing, lane selection, and capacity allocation decisions.
3. Continue monitoring preventive maintenance performance, given the weak relationship between truck age and maintenance cost per mile.
4. Review preventable safety incidents to identify recurring causes and potential training or process improvements.
5. Avoid over-interpreting driver or truck-level fuel differences until route, load, and operating conditions are controlled for.

## Repository Structure

```text
Logistics Analysis/
├── README.md
│
├── data/
│   ├── raw/
│   │   └── original CSV files
│   └── cleaned/
│       └── cleaned tables + master_trip_table.csv
│
├── scripts/
│   ├── 00_profile_data.py
│   ├── 01_clean_data.py
│   ├── 02_build_master_table.py
│   ├── 03_eda_visualize.py
│   └── build_report.js
│
└── outputs/
    ├── figures/
    │   └── 12 analysis charts
    │
    └── reports/
        ├── 00_profile_log.txt
        ├── 01_cleaning_log.txt
        ├── 03_eda_summary.txt
        ├── Logistics_Fleet_Analysis_Report.docx
        └── Logistics_Fleet_Analysis_Report.pdf
```

## Reproducibility

### Requirements

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

The project uses:

- Python 3
- Pandas
- NumPy
- Matplotlib
- Seaborn
- JavaScript / Node.js
- docx
- Git

### Run the Analysis

From the project root:

```bash
python scripts/00_profile_data.py
python scripts/01_clean_data.py
python scripts/02_build_master_table.py
python scripts/03_eda_visualize.py
node scripts/build_report.js
```

The workflow is designed so that the raw data remains unchanged while cleaned datasets, visualizations, analysis outputs, and reports are generated separately.

## Outputs

The project produces:

- Cleaned CSV datasets
- `master_trip_table.csv`
- Data-quality profiling logs
- Cleaning logs
- EDA summary
- 12 analytical visualizations
- Final Word report
- Final PDF report

## Project Purpose

This project demonstrates an end-to-end approach to operational data analysis, from raw relational data and data-quality assessment through cleaning, transformation, exploratory analysis, KPI evaluation, visualization, and business recommendations.

The workflow is designed to be reproducible and adaptable to other operational datasets.

## Author

Built by **[Buhle Mngomezulu]** — [GitHub](https://github.com/buhlemngomezulu-web)
