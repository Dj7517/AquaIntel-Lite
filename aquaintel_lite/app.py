import streamlit as st
import pandas as pd
import numpy as np
import io
from utils.config import TANK_CAPACITY_LITERS, IDEAL_LITERS_PER_PERSON_PER_DAY, APP_TITLE
from utils.data_utils import calculate_metrics, get_summary_stats, top_consumers, compute_top_contribution
from models.ml_model import run_kmeans, predict_tank_empty, generate_alerts
from utils.charts import (
    bar_chart_usage, scatter_cluster, donut_cluster_dist,
    usage_breakdown_stacked, gauge_tank
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AquaIntel Lite",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("💧 AquaIntel Lite Smart Water Intelligence Dashboard ")




# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Space+Grotesk:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    background-color: #0a0f1e !important;
    color: #e2e8f0;
    font-family: 'Space Grotesk', sans-serif;
}

.stApp { background: linear-gradient(135deg, #0a0f1e 0%, #0d1829 50%, #0a1628 100%); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1829 !important;
    border-right: 1px solid #1e293b;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1f3d, #0d1829);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] label { color: #64748b !important; font-size: 12px !important; }
div[data-testid="metric-container"] div[data-testid="metric-value"] {
    color: #06b6d4 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.8rem !important;
}

/* Headers */
h1 { 
    font-family: 'IBM Plex Mono', monospace !important;
    color: #06b6d4 !important; 
    letter-spacing: -1px;
}
h2, h3 { color: #94a3b8 !important; font-size: 0.85rem !important; letter-spacing: 2px; text-transform: uppercase; }

/* Cards */
.aqua-card {
    background: linear-gradient(135deg, #0f1f3d 0%, #0d1829 100%);
    border: 1px solid #1e3a5f;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.alert-card {
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 4px solid;
    font-size: 0.9rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #0891b2, #0e7490) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 1px;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Tables */
.dataframe { background: #0d1829 !important; color: #e2e8f0 !important; }
thead tr th { background: #0f1f3d !important; color: #06b6d4 !important; }

/* Inputs */
.stNumberInput input, .stSelectbox div, .stTextInput input {
    background: #0f1f3d !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
}

/* Divider */
hr { border-color: #1e293b !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] { background: #0d1829; border-bottom: 1px solid #1e293b; }
.stTabs [data-baseweb="tab"] { color: #64748b !important; }
.stTabs [aria-selected="true"] { color: #06b6d4 !important; border-bottom: 2px solid #06b6d4 !important; }

</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
#def load_default_data() -> pd.DataFrame:
#   return pd.read_csv("data/sample_data.csv")
import os

def load_default_data() -> pd.DataFrame:
    BASE_DIR = os.path.dirname(__file__)
    file_path = os.path.join(BASE_DIR, "data", "sample_data.csv")
    return pd.read_csv(file_path)



def render_alert(alert: dict):
    bg = alert["color"] + "22"
    border = alert["color"]
    st.markdown(
        f'<div class="alert-card" style="background:{bg};border-left-color:{border};">'
        f'<b>{alert["level"]}</b> &nbsp; {alert["message"]}</div>',
        unsafe_allow_html=True,
    )


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💧 AquaIntel Lite")
    st.markdown('<div style="color:#475569;font-size:0.75rem;margin-bottom:20px;">Apartment Water Intelligence</div>', unsafe_allow_html=True)
    st.divider()

    data_source = st.radio("📂 Data Source", ["Use Sample Dataset", "Upload CSV", "Manual Entry"])
    st.divider()

    tank_cap = st.number_input("🪣 Tank Capacity (L)", value=TANK_CAPACITY_LITERS, step=500)
    ideal_ppl = st.number_input("💡 Ideal L / Person / Day", value=IDEAL_LITERS_PER_PERSON_PER_DAY, step=5)
    st.divider()

    st.markdown('<div style="color:#475569;font-size:0.75rem;">i2I Challenge 3.0 · Wipro Earthian<br>IIT Madras · Water Intelligence</div>', unsafe_allow_html=True)


# ── Load Data ──────────────────────────────────────────────────────────────────
df_raw = None

if data_source == "Use Sample Dataset":
    df_raw = load_default_data()

elif data_source == "Upload CSV":
    uploaded = st.file_uploader("Upload your flat usage CSV", type=["csv"])
    if uploaded:
        df_raw = pd.read_csv(uploaded)
    else:
        st.info("⬆️ Please upload a CSV with columns: Flat, Residents, Shower_Min, Kitchen_Use_L, Laundry_Use_L, Total_Liters")

elif data_source == "Manual Entry":
    st.subheader("➕ Add Flat Data")
    with st.form("manual_form"):
        col1, col2 = st.columns(2)
        with col1:
            flat_id = st.text_input("Flat Number", "A101")
            residents = st.number_input("Residents", 1, 20, 3)
            shower_min = st.number_input("Shower (mins/day)", 0, 120, 20)
        with col2:
            kitchen_l = st.number_input("Kitchen Use (L)", 0, 500, 140)
            laundry_l = st.number_input("Laundry Use (L)", 0, 500, 100)
        submitted = st.form_submit_button("➕ Add Flat")

    if submitted:
        shower_l = shower_min * 8
        total_l = shower_l + kitchen_l + laundry_l
        new_row = {
            "Flat": flat_id, "Residents": residents,
            "Shower_Min": shower_min, "Kitchen_Use_L": kitchen_l,
            "Laundry_Use_L": laundry_l, "Total_Liters": total_l
        }
        if "manual_df" not in st.session_state:
            st.session_state.manual_df = pd.DataFrame(columns=new_row.keys())
        st.session_state.manual_df = pd.concat(
            [st.session_state.manual_df, pd.DataFrame([new_row])], ignore_index=True
        )

    if "manual_df" in st.session_state and not st.session_state.manual_df.empty:
        df_raw = st.session_state.manual_df.copy()
        if st.button("🗑️ Clear All"):
            del st.session_state.manual_df
            st.rerun()
    else:
        st.warning("No data entered yet. Add at least one flat.")


# ── Main Dashboard ─────────────────────────────────────────────────────────────
if df_raw is None or df_raw.empty:
    st.markdown("""
    <div style="text-align:center;padding:80px 0;color:#475569;">
        <div style="font-size:3rem;">💧</div>
        <h1 style="color:#06b6d4 !important;font-size:2rem;">AquaIntel Lite</h1>
        <p style="font-size:1.1rem;">Apartment Water Intelligence Dashboard</p>
        <p style="color:#334155;">Select a data source from the sidebar to begin.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Process data
df = calculate_metrics(df_raw.copy())
df["Ideal_Usage_L"] = df["Residents"] * ideal_ppl
df = run_kmeans(df)
stats = get_summary_stats(df)
total_usage = df["Total_Liters"].sum()   #fixed 
prediction = predict_tank_empty(total_usage, tank_cap) #fixed
alerts = generate_alerts(df)

# ── Title ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:8px;">
    <span style="font-family:'IBM Plex Mono',monospace;font-size:2rem;font-weight:600;color:#06b6d4;">
        💧 AquaIntel <span style="color:#0ea5e9;">Lite</span>
    </span>
    <span style="color:#475569;font-size:0.85rem;margin-left:12px;">Apartment Water Intelligence Dashboard</span>
</div>
<hr>
""", unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("🏢 Total Flats", stats["total_flats"])
k2.metric("💧 Total Usage / Day", f"{stats['total']:,}L")
k3.metric("📊 Avg per Flat", f"{stats['average']:,}L")
k4.metric("🔴 Overusing Flats", f"{stats['overusers']} / {stats['total_flats']}")
k5.metric("⏳ Tank Lasts", f"{prediction['days']} days" if prediction['days'] else "N/A")

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Usage Overview", "🧠 AI Clustering", "🚨 Alerts", "🔮 Prediction", "📋 Raw Data"
])

# ── Tab 1: Usage Overview ─────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown("### Flat-wise Daily Water Consumption")
        st.plotly_chart(bar_chart_usage(df), use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown("### Top 3 Consumers")
        top3 = top_consumers(df, 3)
        for _, row in top3.iterrows():
            pct_color = "#ef4444" if row["Deviation_Pct"] > 50 else "#f59e0b" if row["Deviation_Pct"] > 20 else "#22c55e"
            st.markdown(f"""
            <div class="aqua-card" style="margin-bottom:10px;padding:14px 18px;">
                <b style="color:#06b6d4;font-family:'IBM Plex Mono',monospace;">{row['Flat']}</b>
                <span style="float:right;color:{pct_color};font-size:0.85rem;">
                    {'+' if row['Deviation_Pct'] > 0 else ''}{row['Deviation_Pct']}% avg
                </span><br>
                <span style="color:#94a3b8;font-size:0.85rem;">
                    {row['Total_Liters']}L · {row['Residents']} residents · {row['Usage_Per_Person']}L/person
                </span>
            </div>
            """, unsafe_allow_html=True)

        top3_pct = compute_top_contribution(df)
        st.markdown(f"""
        <div style="background:#1e1f3a;border:1px solid #3730a3;border-radius:10px;padding:14px;text-align:center;">
            <div style="color:#818cf8;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;">Top 3 flats consume</div>
            <div style="color:#a5b4fc;font-size:2rem;font-family:'IBM Plex Mono',monospace;font-weight:600;">{top3_pct}%</div>
            <div style="color:#475569;font-size:0.75rem;">of total building usage</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Usage Breakdown by Category")
    if "Shower_L" in df.columns:
        st.plotly_chart(usage_breakdown_stacked(df), use_container_width=True, config={"displayModeBar": False})


# ── Tab 2: AI Clustering ───────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="aqua-card">
        <b style="color:#06b6d4;">🧠 K-Means Clustering</b>
        <p style="color:#64748b;font-size:0.85rem;margin:4px 0 0 0;">
        Flats are automatically grouped into 3 efficiency tiers based on total usage and per-person consumption.
        No manual thresholds — the AI finds natural groupings.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Cluster Scatter Plot")
        st.plotly_chart(scatter_cluster(df), use_container_width=True, config={"displayModeBar": False})

    with col2:
        st.markdown("### Distribution")
        st.plotly_chart(donut_cluster_dist(df), use_container_width=True, config={"displayModeBar": False})

        for label, grp in df.groupby("Cluster_Label"):
            color = grp["Cluster_Color"].iloc[0]
            flats = ", ".join(grp["Flat"].tolist())
            st.markdown(f"""
            <div style="background:{color}15;border:1px solid {color}44;border-radius:8px;padding:10px 14px;margin:6px 0;">
                <b style="color:{color};">{label}</b>
                <div style="color:#94a3b8;font-size:0.8rem;margin-top:4px;">{flats}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 3: Alerts ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown("### 🚨 Smart Alerts & Insights")

    if not alerts:
        st.success("✅ No critical alerts. All flats within acceptable usage range.")
    else:
        for alert in alerts:
            render_alert(alert)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Flat-by-Flat Status")

    for _, row in df.sort_values("Total_Liters", ascending=False).iterrows():
        status = "🔴" if row["Total_Liters"] > row["Ideal_Usage_L"] * 1.5 else \
                 "🟡" if row["Total_Liters"] > row["Ideal_Usage_L"] else "🟢"
        deviation_str = f"+{row['Deviation_Pct']}%" if row["Deviation_Pct"] > 0 else f"{row['Deviation_Pct']}%"
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
        col1.markdown(f"<span style='font-size:1.2rem;'>{status}</span>", unsafe_allow_html=True)
        col2.markdown(f"**{row['Flat']}** ({row['Residents']} residents)")
        col3.markdown(f"`{row['Total_Liters']}L` used · `{row['Ideal_Usage_L']}L` ideal")
        col4.markdown(f"<span style='color:#94a3b8;'>{deviation_str} vs avg</span>", unsafe_allow_html=True)


# ── Tab 4: Prediction ─────────────────────────────────────────────────────────
with tab4:
    st.markdown("### 🔮 Tank Depletion Prediction")

    col_g, col_txt = st.columns([1, 2])

    with col_g:
        st.plotly_chart(gauge_tank(max(0, prediction["tank_pct_remaining"])), use_container_width=True, config={"displayModeBar": False})

    with col_txt:
        days = prediction["days"]
        daily = prediction["daily_usage"]
        pct = prediction["tank_pct_remaining"]

        status_color = "#22c55e" if days and days > 3 else "#f59e0b" if days and days > 1.5 else "#ef4444"
        status_text = "🟢 Safe" if days and days > 3 else "🟡 Monitor" if days and days > 1.5 else "🔴 Critical"

        st.markdown(f"""
        <div class="aqua-card">
            <div style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;">Status</div>
            <div style="color:{status_color};font-size:1.5rem;font-weight:700;">{status_text}</div>
            <br>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div>
                    <div style="color:#475569;font-size:0.75rem;">Daily Consumption</div>
                    <div style="color:#06b6d4;font-family:'IBM Plex Mono',monospace;font-size:1.3rem;">{daily:,}L</div>
                </div>
                <div>
                    <div style="color:#475569;font-size:0.75rem;">Tank Remaining</div>
                    <div style="color:#06b6d4;font-family:'IBM Plex Mono',monospace;font-size:1.3rem;">{pct}%</div>
                </div>
                <div>
                    <div style="color:#475569;font-size:0.75rem;">Tank Capacity</div>
                    <div style="color:#e2e8f0;font-family:'IBM Plex Mono',monospace;">{tank_cap:,}L</div>
                </div>
                <div>
                    <div style="color:#475569;font-size:0.75rem;">Days Remaining</div>
                    <div style="color:{status_color};font-family:'IBM Plex Mono',monospace;font-size:1.3rem;">{days} days</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if days and days <= 2:
            st.error(f"⚠️ Tank may empty in {days} days! Notify residents to reduce usage immediately.")
        elif days and days <= 3:
            st.warning(f"🟡 Tank has {days} days at current usage rate. Consider conservation measures.")
        else:
            st.success(f"✅ Tank is sufficient for {days} days at current consumption.")

    # Projection table
    st.markdown("### Daily Projection")
    proj_rows = []
    remaining = tank_cap
    for day in range(1, min(8, int(days or 7) + 2)):
        remaining = max(0, remaining - daily)
        proj_rows.append({"Day": f"Day {day}", "Remaining (L)": f"{remaining:,.0f}", "% Full": f"{remaining/tank_cap*100:.1f}%"})
    st.table(pd.DataFrame(proj_rows))


# ── Tab 5: Raw Data ────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📋 Full Dataset")
    display_cols = ["Flat", "Residents", "Shower_Min", "Kitchen_Use_L", "Laundry_Use_L",
                    "Total_Liters", "Ideal_Usage_L", "Usage_Per_Person", "Deviation_Pct", "Cluster_Label"]
    show_cols = [c for c in display_cols if c in df.columns]
    st.dataframe(df[show_cols], use_container_width=True, height=420)

    csv_data = df[show_cols].to_csv(index=False)
    st.download_button(
        label="⬇️ Download Processed CSV",
        data=csv_data,
        file_name="aquaintel_processed.csv",
        mime="text/csv",
    )
