# Logistics Fleet Performance Analysis — Project Template

A complete data analysis project: profiling → cleaning → joining → EDA/visualization → report.
Use this folder structure and script sequence as a starting template for future projects.

## Folder structure

```
project/
├── data/
│   ├── raw/            original CSVs, untouched (14 source tables)
│   └── cleaned/         cleaned tables + master_trip_table.csv (analysis-ready fact table)
├── scripts/
│   ├── 00_profile_data.py       data quality profiling (missing values, dupes, outliers)
│   ├── 01_clean_data.py         cleaning, with every decision documented in comments
│   ├── 02_build_master_table.py joins cleaned tables into one trip-level fact table
│   ├── 03_eda_visualize.py      EDA + generates all 12 charts
│   └── build_report.js          compiles the final Word report (docx-js)
└── outputs/
    ├── figures/          12 PNG charts at report resolution
    └── reports/
        ├── 00_profile_log.txt              raw profiling output
        ├── 01_cleaning_log.txt             cleaning decisions log
        ├── 03_eda_summary.txt              key stats pulled during EDA
        ├── Logistics_Fleet_Analysis_Report.docx   final report (Word)
        └── Logistics_Fleet_Analysis_Report.pdf    same report, PDF
```

## How to reuse this template on a new dataset

1. Drop new CSVs into `data/raw/`.
2. Edit `00_profile_data.py`: update the `files` dict (table name → filename) and `pk_map`
   (table name → primary key column). Run it first, always — it tells you what actually
   needs cleaning instead of guessing.
3. Edit `01_clean_data.py` based on what profiling found. Document *why* for every
   decision (keep vs. drop nulls, cap vs. flag outliers, etc.) — that documentation is
   what makes the project useful as a reference later.
4. Edit `02_build_master_table.py` to join your tables into whatever the natural
   "one row per unit of analysis" fact table is for your domain (here: one row per trip).
5. Edit `03_eda_visualize.py` — reuse the chart patterns (trend lines, top/bottom-N bars,
   scatter with color-coded third variable, correlation heatmap) against your own columns.
   Keep every chart's takeaway logged to a summary text file as you go — it's the fastest
   way to draft the report narrative afterward without re-deriving numbers from scratch.
6. Edit `build_report.js` — swap the narrative text and image filenames; the section
   structure (Executive Summary → Data Overview → Cleaning → Findings → Recommendations
   → Appendix) works for most analysis projects, not just logistics.

## Notes on chart design decisions worth reusing

- Avoid dual-axis (twin y-axis) charts when the two series have very different scales —
  they can make ordinary fluctuations look like anomalies. Stacked subplots sharing an
  x-axis are safer and just as compact (see chart 1).
- Always call `fig.tight_layout()` before `savefig()` on multi-panel figures, or long
  axis labels on one subplot can visually bleed into the next.
- Flag statistical outliers with a boolean column rather than silently dropping them —
  in this dataset the "outliers" turned out to be real high-cost events, not data errors.

## Key numbers from this run (for quick reference)

- Analysis period: Jan 2022 – Dec 2024
- 85,410 loads/trips, $262.5M revenue, 122.2M miles
- On-time delivery: 44.6% overall — flat across drivers/routes/facilities/detention,
  pointing to a scheduling-window issue rather than an execution issue
- Fleet utilization: 83% average
- Total fuel spend: $95.6M · Total maintenance spend: $5.7M · Safety claims: $2.65M
