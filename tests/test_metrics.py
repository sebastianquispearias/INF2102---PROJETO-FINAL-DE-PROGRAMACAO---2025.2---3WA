import pandas as pd
from src.metrics import compute_basic_stats, compute_vehicle_ranking

def test_compute_basic_stats_simple():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=3, freq="H"),
        "vehicle_id": ["A", "A", "B"],
        "NOx": [10, 20, 30],
        "O2": [20, 20, 20],
        "latitude": [0, 0, 0],
        "longitude": [0, 0, 0],
    })
    stats = compute_basic_stats(df)
    assert stats["n_vehicles"] == 2
    assert stats["n_records"] == 3

def test_compute_vehicle_ranking_threshold():
    df = pd.DataFrame({
        "timestamp": pd.date_range("2025-01-01", periods=4, freq="H"),
        "vehicle_id": ["A", "A", "B", "B"],
        "NOx": [10, 60, 70, 40],
        "O2": [20, 20, 20, 20],
        "latitude": [0, 0, 0, 0],
        "longitude": [0, 0, 0, 0],
    })
    ranking = compute_vehicle_ranking(df, threshold=50)
    assert set(ranking.columns) >= {
        "vehicle_id",
        "mean_nox",
        "median_nox",
        "fraction_time_above_threshold"
    }
