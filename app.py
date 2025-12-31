import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Insight System", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp { background-color: #f6f8fc; }
.card {
    background: #ffffff;
    padding: 18px;
    border-radius: 12px;
}
.big {
    font-size: 32px;
    font-weight: 700;
}
.small {
    font-size: 13px;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
file = st.file_uploader("Upload CSV or Excel dataset", type=["csv", "xlsx"])

if not file:
    st.info("Upload a dataset to begin analysis.")
    st.stop()

# ---------------- LOAD DATA ----------------
df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

dataset_title = os.path.splitext(file.name)[0].replace("_", " ").replace("-", " ").title()
st.title(f"📊 {dataset_title}")
st.caption("Automated insights generated directly from your dataset")

# ---------------- NUMERIC COLUMN DETECTION ----------------
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

if not numeric_cols:
    st.error("No numeric columns found in this dataset.")
    st.stop()

metric = st.selectbox("Select column to analyze", numeric_cols)
series = df[metric].dropna()

# ---------------- CHART SELECTION ----------------
chart_type = st.selectbox(
    "Select chart type",
    [
        "Line (Trend)",
        "Bar (Comparison)",
        "Scatter (Relationship)",
        "Area (Magnitude)",
        "Step (Change Points)",
        "Histogram (Distribution)",
        "Box (Outliers)",
        "Rolling Average (Smoothed Trend)",
        "Cumulative Sum (Progression)"
    ]
)

# ---------------- METRICS ----------------
total = series.sum()
avg = series.mean()
growth = ((series.iloc[-1] - series.iloc[0]) / abs(series.iloc[0])) * 100 if series.iloc[0] != 0 else 0
volatility = series.std()
trend = "Increasing" if growth > 0 else "Decreasing"

# ---------------- KPI DISPLAY ----------------
st.markdown("## 🔢 Dataset Overview")

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"<div class='card'><div class='big'>{total:.2f}</div><div class='small'>Total {metric}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'><div class='big'>{avg:.2f}</div><div class='small'>Average {metric}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'><div class='big'>{growth:.1f}%</div><div class='small'>Overall Change</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='card'><div class='big'>{trend}</div><div class='small'>Trend Direction</div></div>", unsafe_allow_html=True)

# ---------------- CHART (ALL TYPES IMPLEMENTED) ----------------
st.markdown("## 📈 Visual Analysis")

fig = plt.figure(figsize=(9, 4))
plt.clf()

if chart_type == "Line (Trend)":
    plt.plot(series.values, marker="o")
    plt.ylabel(metric)
    plt.title(f"{metric} Trend")

elif chart_type == "Bar (Comparison)":
    plt.bar(range(len(series)), series.values)
    plt.ylabel(metric)
    plt.title(f"{metric} Comparison")

elif chart_type == "Scatter (Relationship)":
    plt.scatter(range(len(series)), series.values)
    plt.ylabel(metric)
    plt.xlabel("Index")
    plt.title(f"{metric} Relationship")

elif chart_type == "Area (Magnitude)":
    plt.fill_between(range(len(series)), series.values, alpha=0.6)
    plt.ylabel(metric)
    plt.title(f"{metric} Magnitude")

elif chart_type == "Step (Change Points)":
    plt.step(range(len(series)), series.values, where="mid")
    plt.ylabel(metric)
    plt.title(f"{metric} Step Changes")

elif chart_type == "Histogram (Distribution)":
    plt.hist(series.values, bins=25)
    plt.xlabel(metric)
    plt.ylabel("Frequency")
    plt.title(f"{metric} Distribution")

elif chart_type == "Box (Outliers)":
    plt.boxplot(series.values, vert=False)
    plt.xlabel(metric)
    plt.title(f"{metric} Outliers")

elif chart_type == "Rolling Average (Smoothed Trend)":
    rolling = series.rolling(window=5).mean()
    plt.plot(series.values, alpha=0.3, label="Raw")
    plt.plot(rolling.values, linewidth=2, label="Rolling Avg (5)")
    plt.legend()
    plt.ylabel(metric)
    plt.title(f"{metric} Rolling Average")

elif chart_type == "Cumulative Sum (Progression)":
    plt.plot(series.cumsum().values)
    plt.ylabel(f"Cumulative {metric}")
    plt.title(f"Cumulative {metric}")

st.pyplot(fig)
plt.close(fig)

# ---------------- DATA INSIGHT ----------------
st.markdown("## 🧠 What the Data Shows")

if growth < 0:
    st.error(f"`{metric}` shows a decreasing pattern.")
elif volatility > avg:
    st.warning(f"`{metric}` varies significantly across records.")
else:
    st.success(f"`{metric}` remains relatively stable.")

# ---------------- FORECAST ----------------
st.markdown("## 🔮 Trend Direction")

if len(series) < 6:
    st.info("Not enough data points to infer a trend direction.")
else:
    X = np.arange(len(series)).reshape(-1, 1)
    y = series.values.reshape(-1, 1)
    model = LinearRegression().fit(X, y)
    direction = "Upward 📈" if model.coef_[0][0] > 0 else "Downward 📉"
    st.info(f"Expected direction: **{direction}**")
