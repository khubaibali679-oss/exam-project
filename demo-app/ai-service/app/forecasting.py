import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np


def build_features(df: pd.DataFrame, lags: int = 6):
    data = df.copy()
    for i in range(1, lags + 1):
        data[f"lag_{i}"] = data["y"].shift(i)

    data["hour"] = data["ds"].dt.hour
    data["minute"] = data["ds"].dt.minute
    data["dayofweek"] = data["ds"].dt.dayofweek
    data["rolling_mean_3"] = data["y"].rolling(3).mean()
    data = data.dropna().reset_index(drop=True)
    return data


def moving_average_forecast(df: pd.DataFrame, points: int = 6, window: int = 6):
    if df.empty:
        return [0.0] * points

    tail = df["y"].tail(window)
    avg = float(tail.mean()) if not tail.empty else 0.0
    avg = max(avg, 0.0)
    return [round(avg, 2)] * points


def forecast_next_points(df: pd.DataFrame, points: int = 6) -> list:
    if df.empty:
        return [0.0] * points

    # If metric is nearly flat or tiny, use moving average instead of regression
    if len(df) < 12:
        return moving_average_forecast(df, points=points)

    if df["y"].std() < 5:
        return moving_average_forecast(df, points=points)

    feature_df = build_features(df)
    if feature_df.empty:
        return moving_average_forecast(df, points=points)

    feature_cols = [c for c in feature_df.columns if c not in ["ds", "y"]]
    X = feature_df[feature_cols]
    y = feature_df["y"]

    model = LinearRegression()
    model.fit(X, y)

    history = df.copy().reset_index(drop=True)
    preds = []

    for _ in range(points):
        temp = build_features(history)
        if temp.empty:
            return moving_average_forecast(history, points=points)

        latest = temp.iloc[-1:][feature_cols]
        pred = float(model.predict(latest)[0])

        # guardrails
        pred = max(pred, 0.0)

        preds.append(round(pred, 2))

        next_time = history["ds"].iloc[-1] + pd.Timedelta(minutes=5)
        history = pd.concat(
            [history, pd.DataFrame([{"ds": next_time, "y": pred}])],
            ignore_index=True
        )

    return preds
