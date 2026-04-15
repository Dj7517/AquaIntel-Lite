import pandas as pd
import numpy as np
from utils.config import IDEAL_LITERS_PER_PERSON_PER_DAY


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add computed columns to the dataframe."""
    df = df.copy()
    df["Ideal_Usage_L"] = df["Residents"] * IDEAL_LITERS_PER_PERSON_PER_DAY
    df["Usage_Per_Person"] = (df["Total_Liters"] / df["Residents"]).round(1)
    avg = df["Total_Liters"].mean()
    df["Deviation_Pct"] = (((df["Total_Liters"] - avg) / avg) * 100).round(1)
    df["Overuse_Flag"] = df["Total_Liters"] > df["Ideal_Usage_L"]
    df["Shower_L"] = df["Shower_Min"] * 8  # ~8L per minute
    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    """Return key summary statistics."""
    total = df["Total_Liters"].sum()
    avg = df["Total_Liters"].mean()
    max_flat = df.loc[df["Total_Liters"].idxmax(), "Flat"]
    max_val = df["Total_Liters"].max()
    min_flat = df.loc[df["Total_Liters"].idxmin(), "Flat"]
    min_val = df["Total_Liters"].min()
    overusers = df[df["Overuse_Flag"]].shape[0]
    return {
        "total": round(total, 1),
        "average": round(avg, 1),
        "max_flat": max_flat,
        "max_val": max_val,
        "min_flat": min_flat,
        "min_val": min_val,
        "overusers": overusers,
        "total_flats": len(df),
    }


def top_consumers(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Return top-n water consuming flats."""
    return df.nlargest(n, "Total_Liters")[["Flat", "Residents", "Total_Liters", "Usage_Per_Person", "Deviation_Pct"]]


def compute_top_contribution(df: pd.DataFrame, n: int = 3) -> float:
    """Percentage of total usage by top-n flats."""
    top_sum = df.nlargest(n, "Total_Liters")["Total_Liters"].sum()
    total = df["Total_Liters"].sum()
    return round((top_sum / total) * 100, 1)
