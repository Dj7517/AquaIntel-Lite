
# ── Simple Clustering (No sklearn) ─────────────────────
def run_kmeans(df):
    avg = df["Total_Liters"].mean()

    df["Cluster_Label"] = df["Total_Liters"].apply(
        lambda x: "High Usage" if x > avg else "Normal Usage"
    )

    df["Cluster_Color"] = df["Cluster_Label"].map({
        "High Usage": "#ef4444",
        "Normal Usage": "#22c55e"
    })

    return df


# ── Tank Prediction (FIXED) ────────────────────────────
def predict_tank_empty(total_usage, tank_capacity=5000):
    daily_usage = total_usage

    if daily_usage == 0:
        return {
            "days": None,
            "daily_usage": 0,
            "tank_pct_remaining": 100
        }

    days = round(tank_capacity / daily_usage, 2)
    remaining = max(0, tank_capacity - daily_usage)
    pct_remaining = round((remaining / tank_capacity) * 100, 1)

    return {
        "days": days,
        "daily_usage": int(daily_usage),
        "tank_pct_remaining": pct_remaining
    }


# ── Alerts ─────────────────────────────────────────────
def generate_alerts(df):
    alerts = []

    avg = df["Total_Liters"].mean()

    for _, row in df.iterrows():
        if row["Total_Liters"] > avg * 1.3:
            alerts.append({
                "level": "⚠️ High Usage",
                "message": f"{row['Flat']} is using unusually high water ({row['Total_Liters']} L)",
                "color": "#ef4444"
            })

    return alerts

