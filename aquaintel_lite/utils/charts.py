import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

PALETTE = ["#06b6d4", "#0ea5e9", "#6366f1", "#8b5cf6", "#f59e0b", "#ef4444", "#22c55e"]
BG = "rgba(0,0,0,0)"
FONT = dict(family="'IBM Plex Mono', monospace", color="#e2e8f0")


def bar_chart_usage(df: pd.DataFrame) -> go.Figure:
    sorted_df = df.sort_values("Total_Liters", ascending=True)
    colors = sorted_df["Cluster_Color"].tolist()

    fig = go.Figure(go.Bar(
        x=sorted_df["Total_Liters"],
        y=sorted_df["Flat"],
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=sorted_df["Total_Liters"].astype(str) + "L",
        textposition="outside",
        textfont=dict(color="#94a3b8", size=11),
        hovertemplate="<b>%{y}</b><br>Usage: %{x}L<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=FONT,
        xaxis=dict(showgrid=True, gridcolor="#1e293b", zeroline=False, title="Liters / Day"),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=60, t=20, b=30),
        height=max(300, len(df) * 38),
    )
    return fig


def scatter_cluster(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for label, grp in df.groupby("Cluster_Label"):
        fig.add_trace(go.Scatter(
            x=grp["Usage_Per_Person"],
            y=grp["Total_Liters"],
            mode="markers+text",
            name=label,
            text=grp["Flat"],
            textposition="top center",
            marker=dict(size=14, color=grp["Cluster_Color"].iloc[0], line=dict(width=1, color="#0f172a")),
            textfont=dict(size=10, color="#cbd5e1"),
        ))

    fig.update_layout(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=FONT,
        xaxis=dict(title="Liters / Person / Day", showgrid=True, gridcolor="#1e293b"),
        yaxis=dict(title="Total Usage (L)", showgrid=True, gridcolor="#1e293b"),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#334155"),
        margin=dict(l=20, r=20, t=20, b=30),
        height=380,
    )
    return fig


def donut_cluster_dist(df: pd.DataFrame) -> go.Figure:
    counts = df.groupby("Cluster_Label").size().reset_index(name="Count")
    colors = df.drop_duplicates("Cluster_Label").set_index("Cluster_Label")["Cluster_Color"].to_dict()

    fig = go.Figure(go.Pie(
        labels=counts["Cluster_Label"],
        values=counts["Count"],
        hole=0.6,
        marker=dict(colors=[colors.get(l, "#06b6d4") for l in counts["Cluster_Label"]],
                    line=dict(width=2, color="#0f172a")),
        textinfo="label+percent",
        textfont=dict(size=11),
    ))

    fig.update_layout(
        paper_bgcolor=BG,
        font=FONT,
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=260,
    )
    return fig


def usage_breakdown_stacked(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col, label, color in [
        ("Shower_L", "Shower", "#06b6d4"),
        ("Kitchen_Use_L", "Kitchen", "#6366f1"),
        ("Laundry_Use_L", "Laundry", "#f59e0b"),
    ]:
        if col in df.columns:
            fig.add_trace(go.Bar(
                name=label,
                x=df["Flat"],
                y=df[col],
                marker_color=color,
            ))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=FONT,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", title="Liters"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=20, t=20, b=30),
        height=320,
    )
    return fig


def gauge_tank(pct_remaining: float) -> go.Figure:
    color = "#22c55e" if pct_remaining > 50 else "#f59e0b" if pct_remaining > 20 else "#ef4444"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_remaining,
        number={"suffix": "%", "font": {"size": 28, "color": "#e2e8f0"}},
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor="#475569"),
            bar=dict(color=color, thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#1e293b",
            steps=[
                {"range": [0, 20], "color": "rgba(239,68,68,0.15)"},
                {"range": [20, 50], "color": "rgba(245,158,11,0.1)"},
                {"range": [50, 100], "color": "rgba(34,197,94,0.08)"},
            ],
            threshold=dict(line=dict(color="#ef4444", width=3), thickness=0.75, value=20),
        ),
    ))

    fig.update_layout(
        paper_bgcolor=BG,
        font=FONT,
        margin=dict(l=20, r=20, t=20, b=20),
        height=220,
    )
    return fig
