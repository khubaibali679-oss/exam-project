from fastapi import FastAPI
from datetime import datetime, timedelta, timezone

from app.config import WORKLOAD_NAME, NAMESPACE, FORECAST_POINTS, MIN_SAVINGS_MONTHLY
from app.prometheus_client import (
    get_current_cpu_millicores,
    get_current_memory_mib,
    get_current_replicas,
    get_cpu_timeseries,
    get_memory_timeseries,
)
from app.forecasting import forecast_next_points
from app.scaling import recommend_replicas
from app.cost_model import estimate_workload_cost
from app.rightsizing import build_rightsizing

app = FastAPI(title="AI Infrastructure Optimizer")


def get_time_range(hours: int = 6):
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    return start.isoformat(), end.isoformat()


@app.get("/")
def root():
    return {"message": "AI Infrastructure Optimizer Running"}


@app.get("/metrics/current")
def metrics_current():
    return {
        "workload": WORKLOAD_NAME,
        "namespace": NAMESPACE,
        "current_cpu_millicores": round(get_current_cpu_millicores(), 2),
        "current_memory_mib": round(get_current_memory_mib(), 2),
        "current_replicas": get_current_replicas()
    }


@app.get("/forecast")
def forecast(workload: str = WORKLOAD_NAME):
    start, end = get_time_range(hours=6)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    return {
        "workload": WORKLOAD_NAME,
        "forecast_points": preds,
        "unit": "millicores",
        "horizon_minutes": FORECAST_POINTS * 5
    }


@app.get("/recommendations")
def recommendations():
    start, end = get_time_range(hours=6)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()

    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)

    return {
        "workload": WORKLOAD_NAME,
        "current_replicas": current_replicas,
        "predicted_cpu_millicores": round(effective_predicted_cpu, 2),
        "predicted_cpu_per_pod_millicores": scaling["predicted_cpu_per_pod_millicores"],
        "recommended_replicas": scaling["recommended_replicas"],
        "action": scaling["action"],
        "reason": scaling["reason"]
    }


@app.get("/scaling/explain")
def scaling_explain():
    start, end = get_time_range(hours=6)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()
    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)

    return {
        "workload": WORKLOAD_NAME,
        "current_replicas": current_replicas,
        "forecast_next_points": preds,
        "current_cpu_millicores": round(current_cpu, 2),
        "predicted_peak_cpu_millicores": round(predicted_peak, 2),
        "effective_predicted_cpu_millicores": round(effective_predicted_cpu, 2),
        "recommended_replicas": scaling["recommended_replicas"],
        "action": scaling["action"],
        "explanation": {
            "formula": "recommended_replicas = ceil(effective_predicted_cpu / cpu_per_pod_millicores)",
            "decision_reason": scaling["reason"]
        }
    }


@app.get("/rightsizing")
def rightsizing():
    start, end = get_time_range(hours=6)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    mem_df = get_memory_timeseries(start, end, step="5m")

    avg_cpu = cpu_df["y"].mean() if not cpu_df.empty else 0.0
    avg_mem = mem_df["y"].mean() if not mem_df.empty else 0.0

    result = build_rightsizing(avg_cpu, avg_mem)
    return {
        "workload": WORKLOAD_NAME,
        **result
    }


@app.get("/cost/summary")
def cost_summary():
    start, end = get_time_range(hours=6)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()
    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)
    cost = estimate_workload_cost(current_replicas, scaling["recommended_replicas"])

    return {
        "workload": WORKLOAD_NAME,
        **cost
    }


@app.get("/cost/recommendations")
def cost_recommendations():
    start, end = get_time_range(hours=6)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    mem_df = get_memory_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()
    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)
    cost = estimate_workload_cost(current_replicas, scaling["recommended_replicas"])

    avg_cpu = cpu_df["y"].mean() if not cpu_df.empty else 0.0
    avg_mem = mem_df["y"].mean() if not mem_df.empty else 0.0
    rightsize = build_rightsizing(avg_cpu, avg_mem)

    recommendations = []

    if scaling["action"] == "scale_down":
        recommendations.append(
            f"Reduce replicas from {current_replicas} to {scaling['recommended_replicas']} based on forecasted demand."
        )
    elif scaling["action"] == "scale_up":
        recommendations.append(
            f"Increase replicas from {current_replicas} to {scaling['recommended_replicas']} to protect performance under predicted demand."
        )

    if rightsize["cpu_status"] == "overprovisioned":
        recommendations.append(
            f"Lower CPU request from {rightsize['requested_cpu_millicores']}m to {rightsize['recommended_cpu_request_millicores']}m."
        )

    if rightsize["memory_status"] == "overprovisioned":
        recommendations.append(
            f"Lower memory request from {rightsize['requested_memory_mib']}Mi to {rightsize['recommended_memory_request_mib']}Mi."
        )

    if cost["estimated_monthly_savings"] < MIN_SAVINGS_MONTHLY:
        recommendations.append("Savings are currently too small for an immediate scaling change; monitor for a longer period.")

    return {
        "workload": WORKLOAD_NAME,
        "recommendations": recommendations,
        "estimated_monthly_savings": cost["estimated_monthly_savings"]
    }
