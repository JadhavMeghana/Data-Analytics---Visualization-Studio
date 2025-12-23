"""
Streamlit Analytics Studio (no Oracle required)
Local, laptop-friendly dashboard for data exploration, KPIs, and charts.
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# Data loading & preparation
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data(uploaded_file: io.BytesIO | None = None, filename: str | None = None) -> pd.DataFrame:
    """
    Load data from uploaded CSV/Excel or bundled sample.
    No strict schema enforced here; mapping is done later.
    """
    if uploaded_file:
        name = (filename or "").lower()
        if name.endswith((".xls", ".xlsx")):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
    else:
        sample_path = Path("data/input/sales_data_sample.csv")
        if sample_path.exists():
            df = pd.read_csv(sample_path)
        else:
            df = generate_sample_data(800)

    # Light normalization to lower-case for convenience (keep originals too)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def generate_sample_data(n_rows: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic sales data for demo purposes.
    """
    np.random.seed(42)
    start_date = pd.Timestamp.now() - pd.Timedelta(days=120)
    customers = list(range(1, 21))
    products = list(range(101, 106))
    regions = [1, 2, 3, 4]

    records = []
    for _ in range(n_rows):
        date = start_date + pd.Timedelta(days=int(np.random.exponential(30)))
        cust = np.random.choice(customers)
        prod = np.random.choice(products)
        region = np.random.choice(regions)
        qty = np.random.randint(1, 50)
        unit_price = np.random.choice([30, 50, 75, 100, 150, 200, 500, 1000])
        discount = np.random.choice([0, 0, 0, 5, 10])
        total = qty * unit_price * (1 - discount / 100)
        records.append(
            {
                "TRANSACTION_DATE": date,
                "CUSTOMER_ID": cust,
                "PRODUCT_ID": prod,
                "QUANTITY": qty,
                "UNIT_PRICE": unit_price,
                "TOTAL_AMOUNT": total,
                "REGION_ID": region,
                "DISCOUNT_PERCENTAGE": discount,
            }
        )
    return pd.DataFrame(records)


# -----------------------------
# KPI calculations
# -----------------------------
def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    df = df.copy()
    total_revenue = df["TOTAL_AMOUNT"].sum()
    total_orders = len(df)
    avg_ticket = df["TOTAL_AMOUNT"].mean()
    unique_customers = df["CUSTOMER_ID"].nunique()
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_ticket": avg_ticket,
        "unique_customers": unique_customers,
    }


def generic_kpis(df: pd.DataFrame, num_col: Optional[str], date_col: Optional[str]) -> Dict[str, object]:
    total_rows = len(df)
    total_cols = len(df.columns)
    stats = {"rows": total_rows, "columns": total_cols}
    if num_col and num_col in df.columns:
        stats.update(
            {
                "sum": df[num_col].sum(),
                "mean": df[num_col].mean(),
                "median": df[num_col].median(),
            }
        )
    if date_col and date_col in df.columns:
        stats.update(
            {
                "min_date": pd.to_datetime(df[date_col]).min(),
                "max_date": pd.to_datetime(df[date_col]).max(),
            }
        )
    return stats


def revenue_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("REGION_ID", dropna=False)["TOTAL_AMOUNT"]
        .sum()
        .reset_index()
        .rename(columns={"TOTAL_AMOUNT": "REVENUE"})
    )


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    m = (
        df.set_index("TRANSACTION_DATE")
        .resample("MS")["TOTAL_AMOUNT"]
        .sum()
        .reset_index()
        .rename(columns={"TOTAL_AMOUNT": "REVENUE"})
    )
    m["PCT_CHANGE"] = m["REVENUE"].pct_change() * 100
    return m


def top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("CUSTOMER_ID")["TOTAL_AMOUNT"]
        .sum()
        .reset_index()
        .rename(columns={"TOTAL_AMOUNT": "REVENUE"})
        .sort_values("REVENUE", ascending=False)
        .head(n)
    )


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("PRODUCT_ID")["TOTAL_AMOUNT"]
        .sum()
        .reset_index()
        .rename(columns={"TOTAL_AMOUNT": "REVENUE"})
        .sort_values("REVENUE", ascending=False)
    )


def detect_outliers(
    df: pd.DataFrame,
    date_col: Optional[str],
    value_col: Optional[str],
    threshold: float = 2.5,
) -> pd.DataFrame:
    """
    Detect outliers on daily aggregated values.
    Works only when both date_col and value_col exist and are numeric/date.
    """
    if not date_col or not value_col:
        return pd.DataFrame()
    if date_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    try:
        tmp = df[[date_col, value_col]].copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna(subset=[date_col, value_col])
        revenue = tmp.groupby(date_col)[value_col].sum().reset_index()
        if len(revenue) < 3:
            return pd.DataFrame()
        z = (revenue[value_col] - revenue[value_col].mean()) / revenue[value_col].std(ddof=0)
        revenue["Z_SCORE"] = z
        revenue["IS_OUTLIER"] = revenue["Z_SCORE"].abs() > threshold
        return revenue[revenue["IS_OUTLIER"]].sort_values(value_col, ascending=False)
    except Exception:
        return pd.DataFrame()


def dataset_summary(df: pd.DataFrame) -> Dict[str, object]:
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "columns_list": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_counts": df.isna().sum().to_dict(),
        "numeric_cols": [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
        "date_like_cols": [c for c in df.columns if "date" in c.lower()],
    }


def build_narrative_summary(
    df: pd.DataFrame,
    date_col: Optional[str],
    num_col: Optional[str],
    cat_cols: List[str],
) -> str:
    rows = len(df)
    cols = len(df.columns)
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    sample_cats = cat_cols[:3] if cat_cols else []

    # Date span
    date_span = None
    if date_col and date_col in df.columns:
        try:
            dates = pd.to_datetime(df[date_col], errors="coerce")
            if not dates.dropna().empty:
                date_span = (dates.min().date(), dates.max().date())
        except Exception:
            date_span = None

    # Numeric stats
    num_stats = None
    if num_col and num_col in df.columns:
        s = pd.to_numeric(df[num_col], errors="coerce")
        s = s.dropna()
        if not s.empty:
            num_stats = (s.min(), s.max(), s.mean())

    # Sample categories and members
    cat_snippets = []
    for c in sample_cats:
        uniq = df[c].dropna().unique().tolist()
        if len(uniq) > 0:
            cat_snippets.append(f"{c} (e.g., {', '.join(map(str, uniq[:5]))})")

    parts = []
    parts.append(f"The dataset contains {rows:,} records with {cols} columns.")
    if date_span:
        parts.append(f"It spans from {date_span[0]} to {date_span[1]} based on '{date_col}'.")
    if num_stats:
        parts.append(
            f"The numeric focus '{num_col}' ranges from {num_stats[0]:,.2f} to {num_stats[1]:,.2f}, "
            f"averaging {num_stats[2]:,.2f}."
        )
    if cat_snippets:
        parts.append(f"Key grouping fields include {', '.join(cat_snippets)}.")
    if not parts:
        parts.append("Upload data and select columns to generate a tailored summary.")

    insight = (
        "Overall insight: This dataset can be explored by the selected date and numeric fields to "
        "see trends over time, and by category fields to compare segments. Use the filters and charts "
        "to spot patterns, outliers, and relationships."
    )

    return " ".join(parts) + " " + insight


# -----------------------------
# Mapping helpers
# -----------------------------
def suggest_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str], List[str]]:
    num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    # Try to parse obvious date-like columns
    if not date_cols:
        for c in df.columns:
            if "date" in c.lower():
                try:
                    df[c] = pd.to_datetime(df[c])
                    date_cols.append(c)
                except Exception:
                    pass
                break
    cat_cols = [c for c in df.columns if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_categorical_dtype(df[c])]
    date_col = date_cols[0] if date_cols else None
    num_col = num_cols[0] if num_cols else None
    return date_col, num_col, cat_cols[:3]


# -----------------------------
# Visualization helpers
# -----------------------------
def card(label: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 16px; border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            ">
            <div style="font-size: 14px; opacity: 0.9;">{label}</div>
            <div style="font-size: 26px; font-weight: 700;">{value}</div>
            <div style="font-size: 12px; opacity: 0.8;">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# Streamlit layout
# -----------------------------
st.set_page_config(
    page_title="Sales Analytics Studio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Data Analytics & Visualization Studio")
st.caption("Local, fast, and flexible analytics workspace")

# Sidebar controls
st.sidebar.header("Data")
uploaded_files = st.sidebar.file_uploader(
    "Upload one or more CSV/XLSX files",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True,
)

st.sidebar.divider()
st.sidebar.header("Filters")
date_range: Tuple[datetime, datetime] | None = None

# Load data (support multiple files up to configured size)
try:
    if not uploaded_files:
        st.warning("Please upload at least one CSV or Excel file to proceed.")
        st.stop()

    if uploaded_files:
        parts = []
        for f in uploaded_files:
            df_part = load_data(f, getattr(f, "name", None))
            df_part["SOURCE_FILE"] = getattr(f, "name", "uploaded.csv")
            parts.append(df_part)
        df_raw = pd.concat(parts, ignore_index=True)

    # Dynamic mapping UI
    st.sidebar.subheader("Column mapping")
    date_suggest, num_suggest, cat_suggest = suggest_columns(df_raw.copy())
    date_col = st.sidebar.selectbox(
        "Date column (optional)",
        options=[None] + list(df_raw.columns),
        index=(list(df_raw.columns).index(date_suggest) + 1) if date_suggest in df_raw.columns else 0,
    )
    num_col = st.sidebar.selectbox(
        "Numeric column (for sums/averages)",
        options=[None] + list(df_raw.columns),
        index=(list(df_raw.columns).index(num_suggest) + 1) if num_suggest in df_raw.columns else 0,
    )
    cat_cols = st.sidebar.multiselect(
        "Category columns (for grouping)",
        options=list(df_raw.columns),
        default=[c for c in cat_suggest if c in df_raw.columns],
    )

    df = df_raw.copy()
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

    # Date filter if date column exists
    if date_col:
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.sidebar.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if date_range and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            df = df[(df[date_col] >= start) & (df[date_col] <= end)]
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

loaded_from = f"{len(uploaded_files)} file(s)"
st.sidebar.success(f"Loaded {len(df):,} rows from {loaded_from}")

# If dataset is empty, stop early
if df.empty:
    st.warning("The dataset is empty. Please upload a valid CSV/XLSX file.")
    st.stop()

# Determine if sales schema is present for legacy charts
sales_required = {"TRANSACTION_DATE", "CUSTOMER_ID", "PRODUCT_ID", "QUANTITY", "UNIT_PRICE", "TOTAL_AMOUNT"}
has_sales_schema = sales_required.issubset(set(df.columns))

# KPIs
col1, col2, col3, col4 = st.columns(4)
if has_sales_schema:
    kpis = compute_kpis(df)
    with col1:
        card("Total Revenue", f"${kpis['total_revenue']:,.0f}", "Sum of total_amount")
    with col2:
        card("Total Orders", f"{kpis['total_orders']:,}", "Row count")
    with col3:
        card("Avg Ticket", f"${kpis['avg_ticket']:,.2f}", "Avg total_amount")
    with col4:
        card("Unique Customers", f"{kpis['unique_customers']:,}", "Distinct customer_id")
else:
    gkpis = generic_kpis(df, num_col, date_col)
    with col1:
        card("Rows", f"{gkpis['rows']:,}", "Total records")
    with col2:
        card("Columns", f"{gkpis['columns']:,}", "Total columns")
    with col3:
        if "sum" in gkpis:
            card("Sum", f"{gkpis['sum']:,.2f}", f"Column: {num_col}")
        else:
            card("Sum", "n/a", "Select a numeric column")
    with col4:
        if "mean" in gkpis:
            card("Mean", f"{gkpis['mean']:,.2f}", f"Column: {num_col}")
        else:
            card("Mean", "n/a", "Select a numeric column")

st.divider()

# Charts
if has_sales_schema:
    left, right = st.columns((2, 1))

    with left:
        st.subheader("Revenue by Region")
        rbr = revenue_by_region(df)
        if len(rbr) > 0:
            fig = px.bar(
                rbr,
                x="REGION_ID",
                y="REVENUE",
                labels={"REGION_ID": "Region", "REVENUE": "Revenue"},
                color="REGION_ID",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No data for revenue by region.")

        st.subheader("Product Performance")
        pp = product_performance(df)
        if len(pp) > 0:
            fig = px.bar(
                pp,
                x="PRODUCT_ID",
                y="REVENUE",
                labels={"PRODUCT_ID": "Product", "REVENUE": "Revenue"},
                color="REVENUE",
                color_continuous_scale="Viridis",
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No product performance data.")

    with right:
        st.subheader("Top Customers")
        top_cust = top_customers(df, 10)
        if len(top_cust) > 0:
            fig = px.bar(
                top_cust,
                x="REVENUE",
                y="CUSTOMER_ID",
                orientation="h",
                labels={"REVENUE": "Revenue", "CUSTOMER_ID": "Customer"},
                color="REVENUE",
                color_continuous_scale="Plasma",
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No customer data.")

    st.subheader("Monthly Revenue Trend")
    trend = monthly_trend(df)
    if len(trend) > 0:
        fig = px.line(
            trend,
            x="TRANSACTION_DATE",
            y="REVENUE",
            markers=True,
            labels={"TRANSACTION_DATE": "Month", "REVENUE": "Revenue"},
        )
        fig.update_traces(line_color="#4e79a7")
        st.plotly_chart(fig, width="stretch")
        st.caption("Pct change vs previous month shown on hover.")
    else:
        st.info("No monthly data available.")
else:
    # Generic charts
    st.subheader("Generic visuals")
    if date_col and num_col and num_col in df.columns and date_col in df.columns:
        fig = px.line(
            df.sort_values(date_col),
            x=date_col,
            y=num_col,
            markers=True,
            labels={date_col: "Date", num_col: num_col},
        )
        st.plotly_chart(fig, width="stretch")
    elif num_col and num_col in df.columns:
        fig = px.histogram(df, x=num_col, nbins=40, title=f"Distribution of {num_col}")
        st.plotly_chart(fig, width="stretch")

    if cat_cols and num_col and num_col in df.columns:
        cat = cat_cols[0]
        agg = (
            df.groupby(cat)[num_col]
            .sum()
            .reset_index()
            .sort_values(num_col, ascending=False)
            .head(15)
        )
        fig = px.bar(agg, x=cat, y=num_col, title=f"Top categories by {num_col}")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Data sample")
    st.dataframe(df.head(200), width="stretch")

# Dataset summary (always shown)
st.divider()
st.subheader("Dataset summary")
summary = dataset_summary(df_raw)
colA, colB, colC = st.columns(3)
with colA:
    st.write("Rows:", f"{summary['rows']:,}")
    st.write("Columns:", f"{summary['columns']:,}")
with colB:
    st.write("Numeric columns:", summary["numeric_cols"])
    st.write("Date-like columns:", summary["date_like_cols"])
with colC:
    st.write("Missing counts (top 10):")
    miss = summary["missing_counts"]
    if miss:
        miss_top = dict(sorted(miss.items(), key=lambda x: x[1], reverse=True)[:10])
        st.json(miss_top)
    else:
        st.write("No missing values reported.")

# Narrative summary
st.subheader("Narrative summary")
st.markdown(build_narrative_summary(df, date_col, num_col, cat_cols))

# Outliers (only when we have a date and numeric)
st.divider()
st.subheader("Outlier detection (daily aggregate)")
outliers = detect_outliers(df, date_col if has_sales_schema else date_col, num_col if has_sales_schema else num_col)
if len(outliers) > 0:
    st.dataframe(outliers, width="stretch")
else:
    st.info("No outliers detected or insufficient data. Select a date column and a numeric column to enable.")

st.divider()

with st.expander("Data preview", expanded=False):
    st.dataframe(df.head(200), width="stretch")

st.success("Streamlit Analytics Studio is ready. Upload your CSV or use the bundled sample data.")

