import pandas as pd
import numpy as np


def forecast_next_points(df: pd.DataFrame, points: int = 6) -> list:
    if df.empty:
        return [0.0] * points

    y = df["y"].astype(float).fillna(0.0)

    if len(y) < 6:
        base = float(y.tail(1).mean()) if len(y) > 0 else 0.0
        return [round(base, 2)] * points

    recent = y.tail(6).to_numpy()
    recent_mean = float(np.mean(recent))
    recent_std = float(np.std(recent))

    # Simple bounded trend using last 2 windows
    prev_window = y.tail(12).head(6).to_numpy() if len(y) >= 12 else recent
    prev_mean = float(np.mean(prev_window)) if len(prev_window) > 0 else recent_mean

    trend = recent_mean - prev_mean

    # Clamp trend so it cannot explode
    max_trend_step = max(20.0, recent_mean * 0.15)
    trend = max(min(trend, max_trend_step), -max_trend_step)

    preds = []
    current = recent_mean

    for _ in range(points):
        current = current + trend

        # lower bound
        current = max(current, 0.0)

        # upper bound: recent mean + 2 std + some headroom
        upper_bound = max(recent_mean * 1.8, recent_mean + (2 * recent_std) + 50.0)
        current = min(current, upper_bound)

        preds.append(round(current, 2))

    return preds
