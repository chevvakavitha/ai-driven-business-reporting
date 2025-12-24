import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI Business Reporting", layout="wide")

st.title("📊 AI-Driven Business Reporting System")
st.caption("Upload data → Generate insights → Get clear decisions")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.stop()

# ---------------- READ DATA ----------------
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

st.subheader("📁 Data Preview")
st.dataframe(df.head())

# ---------------- COLUMN SELECTION ----------------
st.subheader("⚙️ Analysis Configuration")

all_cols = df.columns.tolist()
num_cols = df.select_dtypes(include=np.number).columns.tolist()

if len(num_cols) == 0:
    st.error("Dataset must contain at least one numeric column.")
    st.stop()

x_col = st.selectbox("Select X-axis column (date or category)", all_cols)
y_col = st.selectbox("Select numeric column to analyze", num_cols)

agg_method = st.selectbox(
    "Aggregation Method",
    ["Sum", "Average", "Count"]
)

chart_type = st.selectbox(
    "Chart Type",
    [
        "Line Chart",
        "Bar Chart",
        "Area Chart",
        "Scatter Plot",
        "Histogram",
        "Box Plot",
        "Rolling Trend"
    ]
)

# ---------------- ACTION BUTTON ----------------
generate = st.button("🚀 Generate Dashboard")

if not generate:
    st.info("Click **Generate Dashboard** to see results.")
    st.stop()

# ---------------- DATA PREPARATION ----------------
df_clean = df[[x_col, y_col]].dropna()

# Convert x_col to datetime if possible
try:
    df_clean[x_col] = pd.to_datetime(df_clean[x_col])
    is_datetime = True
except:
    is_datetime = False

# Aggregate safely
if agg_method == "Sum":
    df_agg = df_clean.groupby(x_col)[y_col].sum().reset_index()
elif agg_method == "Average":
    df_agg = df_clean.groupby(x_col)[y_col].mean().reset_index()
else:
    df_agg = df_clean.groupby(x_col)[y_col].count().reset_index()

df_agg = df_agg.sort_values(x_col)

# Limit categories for visibility
if not is_datetime and len(df_agg) > 20:
    df_agg = df_agg.head(20)

# ---------------- KPIs ----------------
st.subheader("📌 Key Metrics")

total = df_agg[y_col].sum()
average = df_agg[y_col].mean()
latest = df_agg[y_col].iloc[-1]
previous = df_agg[y_col].iloc[-2] if len(df_agg) > 1 else latest
growth = ((latest - previous) / previous) * 100 if previous != 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", f"{total:,.2f}")
c2.metric("Average", f"{average:,.2f}")
c3.metric("Latest", f"{latest:,.2f}")
c4.metric("Growth %", f"{growth:.2f}%", delta=f"{growth:.2f}%")

# ---------------- CHART ----------------
st.subheader("📈 Data Visualization")

fig, ax = plt.subplots(figsize=(6, 3))

# Charts that must use RAW DATA
if chart_type == "Scatter Plot":
    ax.scatter(df_clean[x_col], df_clean[y_col])

elif chart_type == "Histogram":
    ax.hist(df_clean[y_col], bins=20)

elif chart_type == "Box Plot":
    ax.boxplot(df_clean[y_col])

# Charts that must use AGGREGATED DATA
elif chart_type == "Line Chart":
    ax.plot(df_agg[x_col], df_agg[y_col])

elif chart_type == "Bar Chart":
    ax.bar(df_agg[x_col], df_agg[y_col])

elif chart_type == "Area Chart":
    ax.fill_between(range(len(df_agg)), df_agg[y_col], alpha=0.5)
    ax.set_xticks(range(len(df_agg)))
    ax.set_xticklabels(df_agg[x_col], rotation=45)

elif chart_type == "Rolling Trend":
    if len(df_agg) >= 3:
        rolling = df_agg[y_col].rolling(3).mean()
        ax.plot(df_agg[x_col], df_agg[y_col], label="Actual")
        ax.plot(df_agg[x_col], rolling, linestyle="--", label="Trend")
        ax.legend()
    else:
        ax.plot(df_agg[x_col], df_agg[y_col])

ax.set_xlabel(x_col)
ax.set_ylabel(y_col)
st.pyplot(fig)


# ---------------- PREDICTION ----------------
st.subheader("🔮 Prediction (Based on Your Data)")

if len(df_agg) >= 3:
    trend = df_agg[y_col].pct_change().tail(3).mean() * 100
    if trend < 0:
        st.error(f"Projected short-term trend: {trend:.2f}% decline")
    else:
        st.success(f"Projected short-term trend: {trend:.2f}% growth")
else:
    st.warning("Not enough data for prediction (need at least 3 points).")

# ---------------- FINAL DECISIONS ----------------
st.subheader("🧠 Final Decision Summary")

if growth < 0:
    st.write("🔴 Performance declined recently. Immediate investigation required.")
else:
    st.write("🟢 Performance improved compared to previous period.")

if len(df_agg) >= 3 and trend < 0:
    st.write("🟠 Short-term outlook shows risk. Focus on efficiency and demand.")
elif len(df_agg) >= 3:
    st.write("🟢 Short-term outlook is stable. Continue strategy.")

if abs(growth) > 25:
    st.write("🟠 High volatility detected. Monitor closely.")

st.info("All outputs are generated strictly from the uploaded dataset.")
