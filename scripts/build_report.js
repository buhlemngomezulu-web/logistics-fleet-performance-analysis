const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  BorderStyle, PageBreak, TableOfContents, Header, Footer, PageNumber,
} = require("docx");

const FIG = path.join(__dirname, "..", "outputs", "figures");

function img(filename, width, height) {
  return new ImageRun({
    type: "png",
    data: fs.readFileSync(`${FIG}/${filename}`),
    transformation: { width, height },
  });
}

function h1(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 400, after: 200 } });
}
function h2(text) {
  return new Paragraph({ text, heading: HeadingLevel.HEADING_2, spacing: { before: 300, after: 150 } });
}
function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 160 },
  });
}
function bullet(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    bullet: { level: 0 },
    spacing: { after: 80 },
  });
}
function caption(text) {
  return new Paragraph({
    children: [new TextRun({ text, italics: true, size: 20, color: "555555" })],
    alignment: AlignmentType.CENTER,
    spacing: { after: 300 },
  });
}
function imgPara(filename, width, height) {
  return new Paragraph({
    children: [img(filename, width, height)],
    alignment: AlignmentType.CENTER,
    spacing: { before: 150, after: 100 },
  });
}

function statTable(rows) {
  const mkCell = (text, bold, shade) => new TableCell({
    width: { size: 50, type: WidthType.PERCENTAGE },
    shading: shade ? { type: ShadingType.CLEAR, fill: "1B4965" } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, bold, color: shade ? "FFFFFF" : "000000" })],
    })],
  });
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [5000, 5000],
    rows: rows.map(([a, b], i) => new TableRow({
      children: [mkCell(a, i === 0, i === 0), mkCell(b, i === 0, i === 0)],
    })),
  });
}

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 22 } },
    },
  },
  sections: [
    // ---------------------------------------------------------- TITLE PAGE
    {
      properties: { page: { size: { width: 12240, height: 15840 } } },
      children: [
        new Paragraph({ text: "", spacing: { before: 2000 } }),
        new Paragraph({
          children: [new TextRun({ text: "Logistics Fleet Performance Analysis", bold: true, size: 52, color: "1B4965" })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
        }),
        new Paragraph({
          children: [new TextRun({ text: "A Data Cleaning, Exploratory Analysis & KPI Report", size: 28, color: "555555" })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 100 },
        }),
        new Paragraph({
          children: [new TextRun({ text: "Fleet Operations Dataset — January 2022 to December 2024", size: 24, color: "555555", italics: true })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 1200 },
        }),
        new Paragraph({
          children: [new TextRun({ text: "Prepared: August 2026", size: 22, color: "777777" })],
          alignment: AlignmentType.CENTER,
        }),
        new Paragraph({
          children: [new TextRun({ text: "Scope: 14 relational tables · 85,410 loads/trips · 150 drivers · 120 trucks", size: 20, color: "777777" })],
          alignment: AlignmentType.CENTER,
          spacing: { before: 100 },
        }),
        new Paragraph({ children: [new PageBreak()] }),
      ],
    },
    // ---------------------------------------------------------- MAIN BODY
    {
      properties: {},
      headers: {
        default: new Header({
          children: [new Paragraph({
            alignment: AlignmentType.RIGHT,
            children: [new TextRun({ text: "Logistics Fleet Performance Analysis", size: 16, color: "999999" })],
          })],
        }),
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "999999" })],
          })],
        }),
      },
      children: [
        h1("Executive Summary"),
        body("This report analyzes three years (2022–2024) of operational data from a trucking and logistics fleet spanning 14 relational tables: drivers, trucks, trailers, customers, facilities, routes, loads, trips, fuel purchases, maintenance records, delivery events, safety incidents, and pre-aggregated monthly driver/truck metrics. The dataset covers 85,410 completed loads generating $262.5M in revenue over 122.2M miles."),
        body("Headline findings:"),
        bullet("Revenue and volume are stable and mildly seasonal — a consistent ~10-15% dip every February, otherwise flat month to month around $7.3M and 2,380 loads."),
        bullet("On-time delivery performance is the fleet's biggest opportunity: only 44.6% of deliveries arrive on time. Critically, this shortfall is uniform — it does not concentrate in particular drivers, routes, load types, booking types, or detention-time buckets — which points to a systemic scheduling issue (e.g. unrealistic scheduled windows) rather than a localized operational failure."),
        bullet("Fleet utilization is healthy overall (83% average), with only 1.2% of truck-months falling below 50% utilization."),
        bullet("Fuel efficiency and revenue-per-mile are essentially flat across drivers and truck makes (MPG range 6.45–6.57) — there is no meaningful equipment or driver-level fuel efficiency gap to close."),
        bullet("Maintenance cost per mile shows no meaningful relationship with truck age (correlation -0.11), suggesting the preventive maintenance program is controlling age-related cost growth effectively."),
        bullet("170 safety incidents were recorded (about 57/year), 38% flagged preventable, with total claims of $2.65M — roughly 1.0% of total revenue."),
        body("Full methodology, data quality notes, and all supporting charts follow. Cleaned datasets, the analysis master table, and every script used to produce this report are included alongside this document for reuse on future projects."),

        h1("1. Data Overview"),
        body("The source data models a mid-size dedicated/contract trucking operation. The schema and key relationships are summarized below."),
        statTable([
          ["Metric", "Value"],
          ["Analysis period", "Jan 1, 2022 – Dec 31, 2024"],
          ["Loads / Trips (completed)", "85,410"],
          ["Total revenue", "$262,525,800"],
          ["Total miles driven", "122,159,201"],
          ["Drivers / Trucks / Trailers", "150 / 120 / 180"],
          ["Customers / Facilities / Routes", "200 / 50 / 58"],
          ["Fuel purchase transactions", "196,442"],
          ["Maintenance records", "2,920"],
          ["Delivery events (pickup + delivery)", "170,820"],
          ["Safety incidents", "170"],
        ]),
        new Paragraph({ text: "", spacing: { after: 200 } }),
        body("Tables fall into three groups: (1) reference/master data — customers, drivers, trucks, trailers, facilities, routes; (2) transactional data — loads, trips, fuel_purchases, maintenance_records, delivery_events, safety_incidents; and (3) pre-computed monthly rollups — driver_monthly_metrics and truck_utilization_metrics. Referential integrity was verified end-to-end: zero orphaned foreign keys were found anywhere in the dataset."),

        h1("2. Data Cleaning"),
        body("All 14 tables were profiled for missing values, duplicate keys, inconsistent types, and statistical outliers before analysis (see 00_profile_data.py in the scripts folder for the full profiling code and outputs/reports/00_profile_log.txt for the raw findings). Key decisions:"),
        bullet("Date/datetime columns (stored as text in the raw CSVs) were parsed into proper datetime types across all 14 tables."),
        bullet("drivers.termination_date is missing for 82.7% of drivers — this is expected, not an error: it is null exactly when employment_status = 'Active'. Left as-is."),
        bullet("~2% of trips are missing driver_id / truck_id / trailer_id, and ~2% of fuel purchases are missing truck_id / driver_id. All belong to Completed trips (not cancellations), so they look like source linkage gaps. Rows were kept (dropping them would understate revenue and mileage totals) and left as true nulls so joins aren't corrupted; a few charts note reduced sample sizes where relevant."),
        bullet("No full-row duplicates or duplicate primary keys were found in any of the 14 tables."),
        bullet("Extreme values in cargo_damage_cost (36 records), maintenance_cost (2 records) and downtime_hours (6 records) were flagged with boolean outlier columns (IQR × 3 method) rather than removed — on inspection these are real high-cost incidents, not data entry errors, and removing them would understate true operating risk."),
        body("Cleaned tables are written to data/cleaned/ in the accompanying files, one CSV per source table plus master_trip_table.csv — a single trip-level fact table joining loads, routes, customers, trips, drivers, trucks, aggregated fuel spend, and delivery on-time outcomes. That master table drives most of the charts in Section 3."),

        h1("3. Key Findings"),

        h2("3.1 Revenue & Volume Trends"),
        imgPara("01_monthly_revenue_volume.png", 580, 367),
        caption("Figure 1. Monthly revenue and load volume, Jan 2022 – Dec 2024."),
        body("Both revenue and load volume are remarkably stable across the three-year window — there is no growth or decline trend, and no strong seasonality beyond a consistent dip every February (fewer calendar days, ~10-15% below the surrounding months). For a template project this is a useful reminder to plot trend lines on their own natural scale rather than a shared dual axis, which can visually exaggerate ordinary fluctuations into false anomalies."),

        h2("3.2 On-Time Delivery Performance"),
        imgPara("02_on_time_delivery_trend.png", 580, 233),
        caption("Figure 2. On-time delivery rate by month."),
        body("On-time delivery holds in a narrow 42.7%–46.2% band throughout the period — never trending up or down. At an overall 44.6%, more than half of all deliveries miss their scheduled window. We tested whether this concentrates anywhere it could be fixed locally:"),
        bullet("By facility: rates range only from 41.9% (worst) to 47.9% (best) across 50 facilities — a 6-point spread, not a smoking gun."),
        bullet("By load type: Dry Van 44.6% vs Refrigerated 44.7% — no difference."),
        bullet("By booking type: Contract 44.6%, Dedicated 44.5%, Spot 44.8% — no difference."),
        bullet("By detention time at delivery: on-time rate is ~44-45% whether detention was 0 minutes or over 2 hours — counterintuitively, detention does not explain lateness."),
        body("Because the shortfall is spread evenly across every operational dimension we could segment, it looks structural — most plausibly, scheduled delivery windows are set tighter than the network can realistically achieve — rather than a performance problem with specific drivers, lanes, or facilities. This is the single highest-leverage finding in the dataset and is where we'd recommend starting a deeper investigation (see Recommendations)."),

        h2("3.3 Customer Analysis"),
        imgPara("03_customer_revenue.png", 580, 222),
        caption("Figure 3. Revenue by customer type (left) and top 10 customers (right)."),
        body("Revenue is well diversified across the three customer/booking types (Contract $98.7M, Spot $82.9M, Dedicated $80.9M) rather than concentrated in one channel. The top customer, First Group, accounts for $9.1M (3.5% of total revenue) — a healthy level of customer diversification with no single-customer concentration risk. 168 of 200 customers (84%) are currently Active."),

        h2("3.4 Route Profitability"),
        imgPara("04_route_profitability.png", 580, 230),
        caption("Figure 4. Top and bottom 10 lanes by average revenue per mile (lanes with ≥30 loads)."),
        body("Revenue per mile ranges from $1.48 (Las Vegas, NV → New York, NY) up to $2.72 (Philadelphia, PA → New York, NY) among established lanes. The spread (~$1.24/mile between best and worst) is a meaningful profitability lever — long cross-country lanes into low-density destinations tend to sit at the bottom, while short, high-density Northeast corridor lanes sit at the top, consistent with typical trucking rate economics."),

        h2("3.5 Fuel Efficiency"),
        imgPara("05_fuel_efficiency.png", 580, 222),
        caption("Figure 5. Average MPG over time (left) and by truck make (right)."),
        body("Fleet-wide fuel efficiency is flat over time and essentially identical across truck makes (6.49–6.51 MPG) — a ~0.02 MPG spread that isn't operationally meaningful. Total fuel spend across the period was $95.6M at an average $3.90/gallon. There's no efficiency gap to close by favoring one make over another in this dataset; efficiency gains would need to come from route/load optimization rather than equipment choice."),

        h2("3.6 Driver Performance"),
        imgPara("06_driver_performance.png", 430, 318),
        caption("Figure 6. Revenue per mile vs. on-time rate by driver (color = average MPG), drivers with ≥20 trips."),
        body("Among the 124 drivers with sufficient trip volume, revenue-per-mile and MPG cluster tightly (no real outliers to single out for coaching or recognition on those two metrics). On-time rate shows more spread (37%–50%), but doesn't correlate with revenue/mile or MPG — consistent with the Section 3.2 finding that on-time performance is a scheduling issue rather than a driver-execution issue."),

        h2("3.7 Fleet Utilization"),
        imgPara("07_fleet_utilization.png", 580, 222),
        caption("Figure 7. Utilization rate distribution (left) and trend over time (right)."),
        body("Fleet utilization averages 83% and is consistently high — only 41 of 3,312 truck-months (1.2%) fall below 50% utilization. The fleet is being used efficiently; there's little idle-asset cost to recover here."),

        h2("3.8 Maintenance Cost Analysis"),
        imgPara("08_maintenance_analysis.png", 580, 222),
        caption("Figure 8. Maintenance cost per mile vs. truck age (left) and total cost by maintenance type (right)."),
        body("Maintenance cost per mile shows no meaningful relationship with truck age (correlation -0.11) — older trucks in this fleet are not measurably more expensive to maintain than newer ones, which is a good sign for the preventive maintenance program. Preventive, Repair, and Tire work make up the largest cost categories at roughly $900K-$960K each; total maintenance spend across the period was $5.7M."),

        h2("3.9 Safety Incidents"),
        imgPara("09_safety_incidents.png", 580, 234),
        caption("Figure 9. Incidents by type (left) and preventable share (right)."),
        body("170 safety incidents occurred over the three years (roughly 57/year against 150 drivers and 120 trucks). DOT Violations are the most common category (39), followed closely by Equipment Damage and Accidents (35 each). 38% of incidents were flagged preventable. Total claims of $2.65M represent about 1.0% of total revenue — worth monitoring but not currently a dominant cost driver."),

        h2("3.10 Load & Booking Mix"),
        imgPara("10_load_booking_mix.png", 580, 235),
        caption("Figure 10. Revenue share by load type (left) and booking type (right)."),
        body("Freight is split almost evenly between Dry Van and Refrigerated (both ~$130M) and reasonably balanced across Contract, Spot, and Dedicated booking types, with Contract leading. Neither load type nor booking type shows a meaningful difference in revenue-per-mile or on-time performance (Section 3.4, 3.2), so this mix is more a description of the business than a lever for improvement on its own."),

        h2("3.11 Detention Time Impact"),
        imgPara("11_detention_impact.png", 580, 296),
        caption("Figure 11. On-time delivery rate by detention-time bucket at the delivery stop."),
        body("Perhaps the most counterintuitive result in the dataset: on-time delivery rate is essentially flat (~44-45%) regardless of how much detention time was logged at the delivery stop, including loads with over two hours of detention. This reinforces the Section 3.2 conclusion — detention is not the mechanism behind the on-time shortfall."),

        h2("3.12 KPI Correlations"),
        imgPara("12_correlation_heatmap.png", 430, 395),
        caption("Figure 12. Correlation matrix across core trip-level KPIs."),
        body("As expected, revenue correlates strongly with distance and duration (0.92-0.93) — longer hauls simply generate more revenue. Revenue-per-mile has a moderate positive correlation with total revenue (0.38) but is essentially uncorrelated with distance, duration, MPG, fuel spend, detention, or weight. No hidden multicollinearity issues were found that would complicate further modeling of this data (e.g. a regression on revenue-per-mile)."),

        h1("4. Recommendations"),
        bullet("Investigate on-time delivery as a scheduling problem, not an execution problem. Since lateness is uniform across drivers, routes, facilities, and detention levels, start by auditing how scheduled_datetime windows are set relative to typical_transit_days and actual_duration_hours — the data suggests targets may be systematically too tight."),
        bullet("Use the route profitability ranking (Section 3.4) to inform lane pricing or capacity allocation — the ~$1.24/mile gap between the best and worst established lanes is a concrete, actionable number for rate negotiations or lane prioritization."),
        bullet("Continue the current preventive maintenance approach — it's successfully decoupling maintenance cost from truck age, which is not a given in most fleets."),
        bullet("Review the 38% preventable-incident share with safety/training teams; even at ~1% of revenue, preventable incidents are the most controllable slice of that $2.65M in claims."),
        bullet("Fuel efficiency and revenue-per-mile are not differentiated by driver or truck make in this data — resist the urge to build incentive programs around either metric until a wider truck-make or route-adjusted analysis justifies it."),

        h1("5. Appendix: Reproducing This Analysis"),
        body("This project follows a standard four-stage structure that can be reused as a template for future data analysis projects:"),
        bullet("scripts/00_profile_data.py — profiles every raw table for shape, dtypes, missing values, duplicates, and outliers."),
        bullet("scripts/01_clean_data.py — applies and documents every cleaning decision, writes cleaned tables to data/cleaned/."),
        bullet("scripts/02_build_master_table.py — joins the cleaned tables into one trip-level analytical fact table with derived KPIs."),
        bullet("scripts/03_eda_visualize.py — runs the exploratory analysis and generates every chart in this report."),
        body("Folder layout:"),
        bullet("data/raw/ — original CSVs, untouched."),
        bullet("data/cleaned/ — cleaned tables plus master_trip_table.csv."),
        bullet("outputs/figures/ — all 12 chart PNGs at report resolution."),
        bullet("outputs/reports/ — profiling log, cleaning log, EDA summary, and this report."),
        body("To adapt this template for a new dataset: update the file paths and column names in scripts 00-02, keep the profiling/cleaning/joining/visualizing sequence, and document every cleaning decision inline as a comment — that documentation is what makes a project genuinely reusable as a reference six months later."),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const REPORTS = path.join(__dirname, "..", "outputs", "reports");
fs.mkdirSync(REPORTS, { recursive: true });

fs.writeFileSync(
  path.join(REPORTS, "Logistics_Fleet_Analysis_Report.docx"),
  buffer
);
  console.log("Report written.");
});
