"""
Warehouse Inventory Analytics Dashboard
Run with: streamlit run app.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    load_data,
    validate_inventory,
    apply_filters,
    compute_overview_kpis,
    discrepancy_rate_by,
    generate_warehouse_insight,
    generate_supplier_insight,
    generate_data_quality_summary,
    generate_business_insights,
)

# ------------------------------------------------------------------------
# PAGE CONFIG & THEME
# ------------------------------------------------------------------------

st.set_page_config(
    page_title="Warehouse Inventory Analytics",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = px.colors.qualitative.Prism
ACCENT = "#4C6EF5"
GOOD = "#2F9E44"
WARN = "#F08C00"
BAD = "#E03131"

CUSTOM_CSS = """
<style>
    .metric-card {
        background: #ffffff;
        border: 1px solid #eaeaea;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .insight-card {
        background: #f4f6fb;
        border-left: 4px solid #4C6EF5;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    section[data-testid="stSidebar"] { background-color: #fafbfd; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------------
# DATA LOAD
# ------------------------------------------------------------------------

raw_df = load_data("inventory_movements.csv")

# ------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ------------------------------------------------------------------------

st.sidebar.title("📦 Filters")
st.sidebar.caption("All charts and KPIs update dynamically.")

min_date = raw_df["movement_date"].min()
max_date = raw_df["movement_date"].max()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date.date(), max_date.date()) if pd.notna(min_date) else None,
    min_value=min_date.date() if pd.notna(min_date) else None,
    max_value=max_date.date() if pd.notna(max_date) else None,
)
if isinstance(date_range, tuple) and len(date_range) != 2:
    date_range = (min_date.date(), max_date.date())

def multiselect_filter(label, col):
    options = sorted(raw_df[col].dropna().unique().tolist())
    return st.sidebar.multiselect(label, options, default=[])

warehouse_sel = multiselect_filter("Warehouse", "warehouse_id")
city_sel = multiselect_filter("Warehouse City", "warehouse_city")
region_sel = multiselect_filter("Region", "region")
type_sel = multiselect_filter("Movement Type", "movement_type")
supplier_sel = multiselect_filter("Supplier", "supplier_id")
sku_sel = st.sidebar.multiselect("SKU", sorted(raw_df["sku_id"].dropna().unique().tolist()), default=[])
status_sel = multiselect_filter("Status", "status")

filters = {
    "date_range": date_range if isinstance(date_range, tuple) else None,
    "warehouse": warehouse_sel,
    "warehouse_city": city_sel,
    "region": region_sel,
    "movement_type": type_sel,
    "supplier": supplier_sel,
    "sku": sku_sel,
    "status": status_sel,
}

df = apply_filters(raw_df, filters)

if st.sidebar.button("Reset Filters"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.download_button(
    "⬇️ Download Filtered Data (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_inventory_movements.csv",
    mime="text/csv",
    use_container_width=True,
)

# ------------------------------------------------------------------------
# NAVIGATION
# ------------------------------------------------------------------------

st.title("📦 Warehouse Inventory Analytics Dashboard")
st.caption("Interactive BI dashboard for operations & supply-chain teams")

PAGES = [
    "Overview",
    "Warehouse Analysis",
    "Supplier Analysis",
    "SKU Analysis",
    "Data Quality",
    "Business Insights",
]
page = st.radio("", PAGES, horizontal=True, label_visibility="collapsed")
st.markdown("---")

if df.empty:
    st.warning("No records match the current filter selection. Adjust filters in the sidebar.")
    st.stop()


# ------------------------------------------------------------------------
# PAGE: OVERVIEW
# ------------------------------------------------------------------------

if page == "Overview":
    kpis = compute_overview_kpis(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Movements", f"{kpis['total_movements']:,}")
    c2.metric("Total Warehouses", kpis["total_warehouses"])
    c3.metric("Total SKUs", kpis["total_skus"])
    c4.metric("Total Suppliers", kpis["total_suppliers"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Avg Unit Cost", f"₹{kpis['avg_unit_cost']:,.2f}")
    c6.metric("Total Inventory Value", f"₹{kpis['total_value']:,.0f}")
    c7.metric("Discrepancy Rate", f"{kpis['discrepancy_rate']:.1f}%")
    c8.metric("Completed Movements", f"{kpis['completed_pct']:.1f}%")

    st.markdown("### Trends & Distributions")
    col1, col2 = st.columns(2)

    with col1:
        monthly = df.groupby("month").size().reset_index(name="movements").sort_values("month")
        fig = px.line(
            monthly, x="month", y="movements", markers=True,
            title="Monthly Movement Trend", color_discrete_sequence=[ACCENT],
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Movements")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        type_dist = df["movement_type"].value_counts().reset_index()
        type_dist.columns = ["movement_type", "count"]
        fig = px.pie(
            type_dist, names="movement_type", values="count", hole=0.55,
            title="Movement Type Distribution", color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        wh_dist = df["warehouse_id"].value_counts().reset_index()
        wh_dist.columns = ["warehouse_id", "count"]
        fig = px.bar(
            wh_dist, x="warehouse_id", y="count", title="Warehouse Distribution",
            color="count", color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        region_dist = df["region"].value_counts().reset_index()
        region_dist.columns = ["region", "count"]
        fig = px.bar(
            region_dist, x="region", y="count", title="Region-wise Movement Distribution",
            color="count", color_continuous_scale="Purples",
        )
        st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------------------
# PAGE: WAREHOUSE ANALYSIS
# ------------------------------------------------------------------------

elif page == "Warehouse Analysis":
    disc_by_wh = discrepancy_rate_by(df, "warehouse_id")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            disc_by_wh, x="discrepancy_rate", y="warehouse_id", orientation="h",
            title="Discrepancy Rate by Warehouse (%)", color="discrepancy_rate",
            color_continuous_scale="Reds",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        total_by_wh = df["warehouse_id"].value_counts().reset_index()
        total_by_wh.columns = ["warehouse_id", "count"]
        fig = px.bar(
            total_by_wh, x="warehouse_id", y="count", title="Total Movements by Warehouse",
            color="count", color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        heat = pd.crosstab(df["warehouse_id"], df["movement_type"])
        fig = px.imshow(
            heat, text_auto=True, aspect="auto",
            title="Warehouse vs Movement Type (Heatmap)", color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        stacked = (
            df[df["status"] == "Discrepancy"]
            .groupby(["movement_type", "warehouse_id"]).size()
            .reset_index(name="discrepancies")
        )
        fig = px.bar(
            stacked, x="movement_type", y="discrepancies", color="warehouse_id",
            title="Discrepancy Counts by Movement Type (Stacked by Warehouse)",
            color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Region-wise Warehouse Comparison")
    region_wh = df.groupby(["region", "warehouse_id"]).size().reset_index(name="movements")
    fig = px.bar(
        region_wh, x="region", y="movements", color="warehouse_id", barmode="group",
        title="Movements by Region & Warehouse", color_discrete_sequence=PALETTE,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔍 Drill Down by Warehouse")
    selected_wh = st.selectbox("Select a Warehouse", sorted(df["warehouse_id"].unique()))
    wh_df = df[df["warehouse_id"] == selected_wh]
    wh_disc = wh_df[wh_df["status"] == "Discrepancy"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Discrepancy Records", f"{len(wh_disc):,}")
    m2.metric("Avg Quantity", f"{wh_df['quantity'].mean():,.1f}")
    m3.metric("Avg Unit Cost", f"₹{wh_df['unit_cost'].mean():,.2f}")
    m4.metric("Inventory Value Affected", f"₹{wh_disc['inventory_value'].sum():,.0f}")

    col5, col6 = st.columns(2)
    with col5:
        st.markdown("**Top 10 SKUs with Discrepancies**")
        top_skus = wh_disc["sku_id"].value_counts().head(10).reset_index()
        top_skus.columns = ["sku_id", "discrepancy_count"]
        st.dataframe(top_skus, use_container_width=True, hide_index=True)

    with col6:
        st.markdown("**Top Suppliers Involved**")
        top_sups = wh_disc["supplier_id"].value_counts().head(10).reset_index()
        top_sups.columns = ["supplier_id", "discrepancy_count"]
        st.dataframe(top_sups, use_container_width=True, hide_index=True)

    st.markdown(
        f'<div class="insight-card">{generate_warehouse_insight(df, selected_wh)}</div>',
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------------
# PAGE: SUPPLIER ANALYSIS
# ------------------------------------------------------------------------

elif page == "Supplier Analysis":
    sup_df = df.dropna(subset=["supplier_id"])

    if sup_df.empty:
        st.info("No supplier-linked movements in the current selection.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.scatter(
                sup_df, x="quantity", y="unit_cost", color="supplier_id",
                title="Quantity vs Unit Cost by Supplier", opacity=0.7,
                color_discrete_sequence=PALETTE,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            avg_cost = sup_df.groupby("supplier_id")["unit_cost"].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(
                avg_cost, x="supplier_id", y="unit_cost", title="Average Unit Cost by Supplier",
                color="unit_cost", color_continuous_scale="Oranges",
            )
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            avg_qty = sup_df.groupby("supplier_id")["quantity"].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(
                avg_qty, x="supplier_id", y="quantity", title="Average Quantity by Supplier",
                color="quantity", color_continuous_scale="Teal",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            overall_avg = sup_df["unit_cost"].mean()
            dev = sup_df.groupby("supplier_id")["unit_cost"].mean() - overall_avg
            dev = dev.sort_values().reset_index()
            dev.columns = ["supplier_id", "deviation"]
            fig = px.bar(
                dev, x="supplier_id", y="deviation",
                title="Supplier Cost Deviation from Overall Average",
                color="deviation", color_continuous_scale="RdBu", color_continuous_midpoint=0,
            )
            st.plotly_chart(fig, use_container_width=True)

        col5, col6 = st.columns(2)
        with col5:
            top_expensive = avg_cost.head(10)
            fig = px.bar(
                top_expensive, x="supplier_id", y="unit_cost",
                title="Top 10 Most Expensive Suppliers", color="unit_cost",
                color_continuous_scale="Reds",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col6:
            fig = px.box(
                sup_df, x="supplier_id", y="unit_cost", title="Unit Cost Distribution by Supplier",
                color="supplier_id", color_discrete_sequence=PALETTE,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Supplier Summary Table")
        summary = sup_df.groupby("supplier_id").agg(
            movements=("movement_id", "count"),
            avg_cost=("unit_cost", "mean"),
            avg_quantity=("quantity", "mean"),
            total_value=("inventory_value", "sum"),
        ).round(2).sort_values("total_value", ascending=False).reset_index()
        st.dataframe(summary, use_container_width=True, hide_index=True)

        st.markdown(
            f'<div class="insight-card">{generate_supplier_insight(df)}</div>',
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------------
# PAGE: SKU ANALYSIS
# ------------------------------------------------------------------------

elif page == "SKU Analysis":
    col1, col2 = st.columns(2)
    with col1:
        disc_skus = (
            df[df["status"] == "Discrepancy"]["sku_id"]
            .value_counts().head(10).reset_index()
        )
        disc_skus.columns = ["sku_id", "discrepancy_count"]
        fig = px.bar(
            disc_skus, x="sku_id", y="discrepancy_count",
            title="Top SKUs with Discrepancies", color="discrepancy_count",
            color_continuous_scale="Reds",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        value_skus = (
            df.groupby("sku_id")["inventory_value"].sum()
            .sort_values(ascending=False).head(10).reset_index()
        )
        fig = px.bar(
            value_skus, x="sku_id", y="inventory_value",
            title="Top High-Value SKUs", color="inventory_value",
            color_continuous_scale="Greens",
        )
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = px.histogram(
            df, x="quantity", nbins=40, title="Quantity Distribution",
            color_discrete_sequence=[ACCENT],
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        count_skus = (
            df["sku_id"].value_counts().head(10).reset_index()
        )
        count_skus.columns = ["sku_id", "movement_count"]
        fig = px.bar(
            count_skus, x="sku_id", y="movement_count",
            title="Top SKUs by Movement Count", color="movement_count",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Searchable SKU Table")
    search = st.text_input("Search by SKU, Warehouse, or Supplier")
    table_cols = ["sku_id", "warehouse_id", "supplier_id", "quantity", "unit_cost",
                  "stock_before", "stock_after", "status"]
    table = df[table_cols].copy()
    if search:
        mask = (
            table["sku_id"].str.contains(search, case=False, na=False)
            | table["warehouse_id"].str.contains(search, case=False, na=False)
            | table["supplier_id"].str.contains(search, case=False, na=False)
        )
        table = table[mask]
    st.dataframe(table, use_container_width=True, hide_index=True, height=420)


# ------------------------------------------------------------------------
# PAGE: DATA QUALITY
# ------------------------------------------------------------------------

elif page == "Data Quality":
    validated = validate_inventory(df)

    missing_total = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())
    missing_supplier = int(df["supplier_id"].isna().sum())
    missing_customer = int(df["customer_id"].isna().sum())
    missing_stock_after = int(df["stock_after"].isna().sum())
    negative_stock = int((df["stock_after"].dropna() < 0).sum())
    invalid_calc = int((validated["calc_valid"] == False).sum())  # noqa: E712

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Missing Values", f"{missing_total:,}")
    c2.metric("Duplicate Rows", f"{duplicates:,}")
    c3.metric("Missing Supplier IDs", f"{missing_supplier:,}")
    c4.metric("Missing Customer IDs", f"{missing_customer:,}")

    c5, c6, c7 = st.columns(3)
    c5.metric("Missing Stock After", f"{missing_stock_after:,}")
    c6.metric("Negative Stock Records", f"{negative_stock:,}")
    c7.metric("Invalid Inventory Calculations", f"{invalid_calc:,}")

    st.markdown("### Missing Values Overview")
    col1, col2 = st.columns(2)
    with col1:
        miss_table = df.isna().sum().reset_index()
        miss_table.columns = ["column", "missing_count"]
        miss_table = miss_table[miss_table["missing_count"] > 0].sort_values(
            "missing_count", ascending=False
        )
        st.dataframe(miss_table, use_container_width=True, hide_index=True)

    with col2:
        fig = px.imshow(
            df.isna().astype(int).T, aspect="auto", title="Missing Values Heatmap",
            color_continuous_scale="Reds",
        )
        fig.update_layout(yaxis_title="Column", xaxis_title="Row Index")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Status Distribution")
    status_dist = df["status"].value_counts().reset_index()
    status_dist.columns = ["status", "count"]
    fig = px.bar(
        status_dist, x="status", y="count", title="Status Distribution",
        color="status", color_discrete_sequence=PALETTE,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Invalid Inventory Calculation Records")
    bad_rows = validated[validated["calc_valid"] == False]  # noqa: E712
    if bad_rows.empty:
        st.success("No invalid inventory calculations detected in the current selection.")
    else:
        st.dataframe(
            bad_rows[["movement_id", "sku_id", "warehouse_id", "movement_type",
                      "stock_before", "quantity", "stock_after", "expected_stock_after"]],
            use_container_width=True, hide_index=True,
        )

    st.markdown(
        f'<div class="insight-card">{generate_data_quality_summary(df, validated)}</div>',
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------------------
# PAGE: BUSINESS INSIGHTS
# ------------------------------------------------------------------------

elif page == "Business Insights":
    insights = generate_business_insights(df)

    labels = {
        "top_discrepancy_warehouse": "🏭 Highest Discrepancy Warehouse",
        "top_value_warehouse": "💰 Highest-Value Warehouse",
        "problem_sku": "⚠️ Most Problematic SKU",
        "top_cost_supplier": "📈 Highest-Cost Supplier",
        "worst_discrepancy_movement": "🔺 Highest-Value Discrepancy Movement",
        "overall_discrepancy_rate": "📊 Overall Discrepancy Rate",
        "top_discrepancy_type": "🔁 Top Discrepancy-Causing Movement Type",
        "recommendation": "✅ Recommendation",
    }

    for key, label in labels.items():
        if key in insights:
            st.markdown(
                f'<div class="insight-card"><strong>{label}</strong><br>{insights[key]}</div>',
                unsafe_allow_html=True,
            )
