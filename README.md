# 📦 Warehouse Inventory Analytics Dashboard

An interactive Streamlit business-intelligence dashboard for analyzing warehouse
inventory movements — built for operations managers to monitor stock accuracy,
supplier performance, SKU health, and overall data quality.

## Features

- **Overview** — headline KPIs, monthly trend, movement-type mix, warehouse & region distribution
- **Warehouse Analysis** — discrepancy rates, heatmaps, and a drill-down view per warehouse with auto-generated insight
- **Supplier Analysis** — cost/quantity scatter, deviation from average, top expensive suppliers, summary table, auto insight
- **SKU Analysis** — top discrepancy/high-value SKUs, quantity distribution, searchable data table
- **Data Quality** — missing-value audit, duplicate detection, stock-calculation validation, invalid-record table
- **Business Insights** — plain-English summary of the five key business questions

All pages respond live to the sidebar filters (date range, warehouse, city, region,
movement type, supplier, SKU, status), and the filtered dataset can be downloaded as CSV
at any time.

## Files

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit application (pages, charts, layout) |
| `Warehouse_inventory_Analytics.ipynb` | Data loading, cleaning, validation, KPI and insight-generation functions |
| `inventory_movements.csv` | Source dataset |
| `requirements.txt` | Python dependencies |

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Make sure `inventory_movements.csv` sits in the
same folder as `app.py` (or edit the path passed to `load_data()` in `app.py`).

## Data Quality Rules Applied

The dashboard validates `stock_after` against the movement type:

- **Inbound / Return:** `stock_after = stock_before + quantity`
- **Outbound:** `stock_after = stock_before - quantity`
- **Transfer / Adjustment:** no fixed rule enforced (informational only)

Rows that fail this check, have missing values, negative stock, or are exact duplicates
are surfaced on the **Data Quality** page.

## Notes

- Chart PNG export is available via the camera icon in each Plotly chart's toolbar
  (requires the `kaleido` package, included in `requirements.txt`).
- Caching (`st.cache_data`) is used for data loading and validation so filtering stays fast.
