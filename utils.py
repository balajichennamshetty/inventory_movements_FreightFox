"""
utils.py
Reusable helper functions for the Warehouse Inventory Analytics Dashboard.
Covers: data loading/cleaning, KPI calculations, data-quality validation,
and text-based business insight generation.
"""

import pandas as pd
import numpy as np
import streamlit as st


# --------------------------------------------------------------------------
# DATA LOADING
# --------------------------------------------------------------------------

@st.cache_data
def load_data(path: str = "inventory_movements.csv") -> pd.DataFrame:
    """Load the raw CSV and perform baseline type conversions."""
    df = pd.read_csv(path)

    # Parse dates (invalid parsing -> NaT, handled gracefully downstream)
    df["movement_date"] = pd.to_datetime(df["movement_date"], errors="coerce")
    df["expected_date"] = pd.to_datetime(df["expected_date"], errors="coerce")

    # Normalize text columns
    for col in ["sku_id", "warehouse_id", "warehouse_city", "region",
                "movement_type", "supplier_id", "customer_id", "status"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()

    # Derived column used everywhere
    df["inventory_value"] = df["quantity"] * df["unit_cost"]
    df["month"] = df["movement_date"].dt.to_period("M").astype(str)

    return df


@st.cache_data
def validate_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flags rows that violate stock_after calculation rules:
      Inbound / Return : stock_after = stock_before + quantity
      Outbound         : stock_after = stock_before - quantity
      Adjustment / Transfer : no fixed rule enforced (informational only)
    Returns the dataframe with an added 'calc_valid' boolean column
    (NaN stock_after rows are treated as unable-to-validate, not invalid).
    """
    df = df.copy()
    expected = np.where(
        df["movement_type"].isin(["Inbound", "Return"]),
        df["stock_before"] + df["quantity"],
        np.where(
            df["movement_type"] == "Outbound",
            df["stock_before"] - df["quantity"],
            np.nan,
        ),
    )
    df["expected_stock_after"] = expected

    has_rule = df["movement_type"].isin(["Inbound", "Return", "Outbound"])
    has_value = df["stock_after"].notna()

    df["calc_valid"] = np.where(
        has_rule & has_value,
        np.isclose(df["stock_after"], df["expected_stock_after"], equal_nan=False),
        np.nan,  # not applicable / not checkable
    )
    return df


# --------------------------------------------------------------------------
# FILTERING
# --------------------------------------------------------------------------

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply the sidebar filter selections to the dataframe."""
    out = df.copy()

    if filters.get("date_range"):
        start, end = filters["date_range"]
        out = out[
            (out["movement_date"].isna())
            | ((out["movement_date"] >= pd.Timestamp(start))
               & (out["movement_date"] <= pd.Timestamp(end)))
        ]

    mapping = {
        "warehouse": "warehouse_id",
        "warehouse_city": "warehouse_city",
        "region": "region",
        "movement_type": "movement_type",
        "supplier": "supplier_id",
        "sku": "sku_id",
        "status": "status",
    }
    for key, col in mapping.items():
        vals = filters.get(key)
        if vals:
            out = out[out[col].isin(vals)]

    return out


# --------------------------------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------------------------------

def compute_overview_kpis(df: pd.DataFrame) -> dict:
    total_movements = len(df)
    total_warehouses = df["warehouse_id"].nunique()
    total_skus = df["sku_id"].nunique()
    total_suppliers = df["supplier_id"].nunique(dropna=True)
    avg_unit_cost = df["unit_cost"].mean() if total_movements else 0
    total_value = df["inventory_value"].sum()

    discrepancy_rate = (
        (df["status"] == "Discrepancy").sum() / total_movements * 100
        if total_movements else 0
    )
    completed_pct = (
        (df["status"] == "Completed").sum() / total_movements * 100
        if total_movements else 0
    )

    return {
        "total_movements": total_movements,
        "total_warehouses": total_warehouses,
        "total_skus": total_skus,
        "total_suppliers": total_suppliers,
        "avg_unit_cost": avg_unit_cost,
        "total_value": total_value,
        "discrepancy_rate": discrepancy_rate,
        "completed_pct": completed_pct,
    }


def discrepancy_rate_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Discrepancy rate (%) grouped by an arbitrary column."""
    grp = df.groupby(group_col, dropna=False).agg(
        total=("status", "size"),
        discrepancies=("status", lambda s: (s == "Discrepancy").sum()),
    )
    grp["discrepancy_rate"] = (grp["discrepancies"] / grp["total"] * 100).round(2)
    return grp.reset_index().sort_values("discrepancy_rate", ascending=False)


# --------------------------------------------------------------------------
# BUSINESS INSIGHTS (auto-generated plain-English text)
# --------------------------------------------------------------------------

def generate_warehouse_insight(df: pd.DataFrame, warehouse_id: str) -> str:
    sub = df[df["warehouse_id"] == warehouse_id]
    if sub.empty:
        return f"No records found for {warehouse_id} under the current filters."

    total = len(sub)
    disc = (sub["status"] == "Discrepancy").sum()
    disc_rate = disc / total * 100 if total else 0
    value = sub["inventory_value"].sum()
    top_type = (
        sub.loc[sub["status"] == "Discrepancy", "movement_type"]
        .mode()
        .iloc[0] if disc > 0 else "N/A"
    )
    top_sku = (
        sub.loc[sub["status"] == "Discrepancy", "sku_id"]
        .mode()
        .iloc[0] if disc > 0 else "N/A"
    )

    return (
        f"**{warehouse_id}** processed **{total:,}** movements worth "
        f"**₹{value:,.0f}** in inventory value. Its discrepancy rate stands at "
        f"**{disc_rate:.1f}%** ({disc:,} flagged records). "
        + (
            f"The most common discrepancy type here is **{top_type}**, and "
            f"**{top_sku}** is the SKU most frequently involved in these issues."
            if disc > 0 else
            "No discrepancies were recorded for this warehouse in the selected period."
        )
    )


def generate_supplier_insight(df: pd.DataFrame) -> str:
    sub = df.dropna(subset=["supplier_id"])
    if sub.empty:
        return "No supplier-linked movements available under the current filters."

    supplier_avg = sub.groupby("supplier_id")["unit_cost"].mean()
    overall_avg = sub["unit_cost"].mean()
    deviation = ((supplier_avg - overall_avg) / overall_avg * 100).sort_values(ascending=False)

    if deviation.empty:
        return "Not enough supplier data to compute cost deviations."

    top_supplier = deviation.index[0]
    top_dev = deviation.iloc[0]
    low_supplier = deviation.index[-1]
    low_dev = deviation.iloc[-1]

    direction_top = "above" if top_dev >= 0 else "below"
    direction_low = "above" if low_dev >= 0 else "below"

    return (
        f"**{top_supplier}** prices are **{abs(top_dev):.1f}% {direction_top}** "
        f"the overall average unit cost (₹{overall_avg:,.2f}), making it the most "
        f"expensive-relative supplier in the current selection. In contrast, "
        f"**{low_supplier}** runs **{abs(low_dev):.1f}% {direction_low}** the average, "
        f"the most cost-competitive supplier. Significant deviations like these are "
        f"worth reviewing for renegotiation or sourcing decisions."
    )


def generate_data_quality_summary(df: pd.DataFrame, df_validated: pd.DataFrame) -> str:
    total = len(df)
    missing_supplier = df["supplier_id"].isna().sum()
    missing_customer = df["customer_id"].isna().sum()
    missing_stock_after = df["stock_after"].isna().sum()
    negative_stock = (df["stock_after"].dropna() < 0).sum()
    duplicates = df.duplicated().sum()
    invalid_calc = (df_validated["calc_valid"] == False).sum()  # noqa: E712

    return (
        f"Out of **{total:,}** total records, **{missing_supplier:,}** are missing a "
        f"supplier ID (expected for internal transfers/adjustments) and "
        f"**{missing_customer:,}** are missing a customer ID (expected for non-outbound "
        f"movements). **{missing_stock_after:,}** records have no recorded post-movement "
        f"stock level, and **{negative_stock:,}** show a negative stock value, which "
        f"should be investigated. **{duplicates:,}** exact duplicate rows were detected. "
        f"Of the records where stock math can be verified, **{invalid_calc:,}** fail the "
        f"expected inbound/outbound/return calculation and should be reconciled."
    )


def generate_business_insights(df: pd.DataFrame) -> dict:
    """Return a dict of headline insight strings for the Business Insights page."""
    insights = {}

    if df.empty:
        return {"empty": "No data available for the selected filters."}

    # Warehouse with highest discrepancy rate
    wh_disc = discrepancy_rate_by(df, "warehouse_id")
    if not wh_disc.empty:
        top_wh = wh_disc.iloc[0]
        insights["top_discrepancy_warehouse"] = (
            f"**{top_wh['warehouse_id']}** has the highest discrepancy rate at "
            f"**{top_wh['discrepancy_rate']:.1f}%** ({int(top_wh['discrepancies'])} of "
            f"{int(top_wh['total'])} movements)."
        )

    # Warehouse contributing highest inventory value
    wh_value = df.groupby("warehouse_id")["inventory_value"].sum().sort_values(ascending=False)
    if not wh_value.empty:
        insights["top_value_warehouse"] = (
            f"**{wh_value.index[0]}** contributes the highest inventory value at "
            f"**₹{wh_value.iloc[0]:,.0f}**."
        )

    # Most problematic SKU (most discrepancies)
    sku_disc = df[df["status"] == "Discrepancy"]["sku_id"].value_counts()
    if not sku_disc.empty:
        insights["problem_sku"] = (
            f"**{sku_disc.index[0]}** is the most problematic SKU, involved in "
            f"**{sku_disc.iloc[0]}** discrepancy records."
        )

    # Supplier with highest average cost
    sup_cost = df.dropna(subset=["supplier_id"]).groupby("supplier_id")["unit_cost"].mean()
    sup_cost = sup_cost.sort_values(ascending=False)
    if not sup_cost.empty:
        insights["top_cost_supplier"] = (
            f"**{sup_cost.index[0]}** has the highest average unit cost at "
            f"**₹{sup_cost.iloc[0]:,.2f}**."
        )

    # Highest-value discrepancy movement
    disc_rows = df[df["status"] == "Discrepancy"]
    if not disc_rows.empty:
        worst = disc_rows.loc[disc_rows["inventory_value"].idxmax()]
        insights["worst_discrepancy_movement"] = (
            f"The highest-value discrepancy is **{worst['movement_id']}** "
            f"({worst['sku_id']} at {worst['warehouse_id']}), worth "
            f"**₹{worst['inventory_value']:,.0f}**."
        )

    # Overall discrepancy rate
    overall_rate = (df["status"] == "Discrepancy").mean() * 100
    insights["overall_discrepancy_rate"] = (
        f"The overall discrepancy rate across all selected movements is "
        f"**{overall_rate:.1f}%**."
    )

    # Top movement type causing discrepancies
    type_disc = disc_rows["movement_type"].value_counts()
    if not type_disc.empty:
        insights["top_discrepancy_type"] = (
            f"**{type_disc.index[0]}** movements account for the largest share of "
            f"discrepancies (**{type_disc.iloc[0]}** records)."
        )

    # Recommendation
    if not wh_disc.empty:
        insights["recommendation"] = (
            f"**Recommendation:** Prioritize a stock-accuracy audit at "
            f"**{wh_disc.iloc[0]['warehouse_id']}** and review handling procedures for "
            f"**{type_disc.index[0] if not type_disc.empty else 'high-risk'}** movements, "
            f"since these concentrate the largest share of inventory discrepancies."
        )

    return insights
