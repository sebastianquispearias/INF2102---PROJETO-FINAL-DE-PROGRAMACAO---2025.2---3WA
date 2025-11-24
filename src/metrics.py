import numpy as np

def compute_basic_stats(df):
    return {
        "global_mean_nox": float(df["NOx"].mean()),
        "global_median_nox": float(df["NOx"].median()),
        "n_vehicles": int(df["vehicle_id"].nunique()),
        "n_records": int(len(df)),
    }

def compute_vehicle_ranking(df, threshold):
    grouped = df.groupby("vehicle_id")
    stats = []

    for vid, g in grouped:
        mean_nox = g["NOx"].mean()
        median_nox = g["NOx"].median()
        fraction_above = np.mean(g["NOx"] > threshold)
        stats.append({
            "vehicle_id": vid,
            "mean_nox": mean_nox,
            "median_nox": median_nox,
            "fraction_time_above_threshold": fraction_above,
        })

    import pandas as pd
    ranking_df = pd.DataFrame(stats)
    ranking_df = ranking_df.sort_values(
        by="fraction_time_above_threshold",
        ascending=False
    )
    return ranking_df
