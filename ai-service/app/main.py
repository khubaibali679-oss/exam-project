from fastapi import FastAPI
from datetime import datetime, timedelta, timezone

from app.config import (
    WORKLOAD_NAME,
    NAMESPACE,
    FORECAST_POINTS,
    MIN_SAVINGS_MONTHLY,
    CPU_PER_POD_MILLICORES,
    MAX_REPLICAS,
)
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


def get_per_pod_rightsizing(hours: int = 1):
    start, end = get_time_range(hours=hours)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    mem_df = get_memory_timeseries(start, end, step="5m")

    current_replicas = max(get_current_replicas(), 1)

    avg_cpu_total = cpu_df["y"].mean() if not cpu_df.empty else 0.0
    avg_mem_total = mem_df["y"].mean() if not mem_df.empty else 0.0

    avg_cpu_per_pod = avg_cpu_total / current_replicas
    avg_mem_per_pod = avg_mem_total / current_replicas

    result = build_rightsizing(avg_cpu_per_pod, avg_mem_per_pod)

    return {
        "lookback_hours": hours,
        "current_replicas": current_replicas,
        "avg_cpu_total_millicores": round(avg_cpu_total, 2),
        "avg_memory_total_mib": round(avg_mem_total, 2),
        "avg_cpu_per_pod_millicores": round(avg_cpu_per_pod, 2),
        "avg_memory_per_pod_mib": round(avg_mem_per_pod, 2),
        **result,
    }


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
        "current_replicas": get_current_replicas(),
    }


@app.get("/forecast")
def forecast():
    start, end = get_time_range(hours=1)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    return {
        "workload": WORKLOAD_NAME,
        "forecast_points": preds,
        "unit": "millicores",
        "horizon_minutes": FORECAST_POINTS * 5,
        "lookback_hours": 1,
    }


@app.get("/recommendations")
def recommendations():
    start, end = get_time_range(hours=1)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()

    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)

    max_modeled_capacity = CPU_PER_POD_MILLICORES * MAX_REPLICAS
    capacity_warning = None

    if effective_predicted_cpu > max_modeled_capacity:
        capacity_warning = (
            f"Predicted CPU {round(effective_predicted_cpu, 2)}m exceeds modeled max "
            f"capacity {max_modeled_capacity}m at MAX_REPLICAS={MAX_REPLICAS}."
        )

    return {
        "workload": WORKLOAD_NAME,
        "current_replicas": current_replicas,
        "predicted_cpu_millicores": round(effective_predicted_cpu, 2),
        "predicted_cpu_per_pod_millicores": scaling["predicted_cpu_per_pod_millicores"],
        "recommended_replicas": scaling["recommended_replicas"],
        "action": scaling["action"],
        "reason": scaling["reason"],
        "capacity_warning": capacity_warning,
    }


@app.get("/scaling/explain")
def scaling_explain():
    start, end = get_time_range(hours=1)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()
    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)

    max_modeled_capacity = CPU_PER_POD_MILLICORES * MAX_REPLICAS
    capacity_warning = None

    if effective_predicted_cpu > max_modeled_capacity:
        capacity_warning = (
            f"Predicted CPU {round(effective_predicted_cpu, 2)}m exceeds modeled max "
            f"capacity {max_modeled_capacity}m at MAX_REPLICAS={MAX_REPLICAS}."
        )

    return {
        "workload": WORKLOAD_NAME,
        "current_replicas": current_replicas,
        "forecast_next_points": preds,
        "current_cpu_millicores": round(current_cpu, 2),
        "predicted_peak_cpu_millicores": round(predicted_peak, 2),
        "effective_predicted_cpu_millicores": round(effective_predicted_cpu, 2),
        "recommended_replicas": scaling["recommended_replicas"],
        "action": scaling["action"],
        "capacity_warning": capacity_warning,
        "explanation": {
            "formula": "recommended_replicas = ceil(effective_predicted_cpu / cpu_per_pod_millicores)",
            "cpu_per_pod_millicores": CPU_PER_POD_MILLICORES,
            "max_replicas": MAX_REPLICAS,
            "decision_reason": scaling["reason"],
        },
    }


@app.get("/rightsizing")
def rightsizing():
    result = get_per_pod_rightsizing(hours=1)
    return {
        "workload": WORKLOAD_NAME,
        **result,
    }


@app.get("/cost/summary")
def cost_summary():
    start, end = get_time_range(hours=1)
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
        **cost,
    }


@app.get("/cost/recommendations")
def cost_recommendations():
    start, end = get_time_range(hours=1)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()
    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)
    cost = estimate_workload_cost(current_replicas, scaling["recommended_replicas"])
    rightsize = get_per_pod_rightsizing(hours=1)

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
    elif rightsize["cpu_status"] == "underprovisioned":
        recommendations.append(
            f"Increase CPU request from {rightsize['requested_cpu_millicores']}m to {rightsize['recommended_cpu_request_millicores']}m."
        )

    if rightsize["memory_status"] == "overprovisioned":
        recommendations.append(
            f"Lower memory request from {rightsize['requested_memory_mib']}Mi to {rightsize['recommended_memory_request_mib']}Mi."
        )
    elif rightsize["memory_status"] == "underprovisioned":
        recommendations.append(
            f"Increase memory request from {rightsize['requested_memory_mib']}Mi to {rightsize['recommended_memory_request_mib']}Mi."
        )

    if cost.get("estimated_monthly_savings", 0) > 0:
        recommendations.append(
            f"Estimated monthly savings: ${cost['estimated_monthly_savings']}."
        )

    if cost.get("estimated_monthly_cost_increase", 0) > 0:
        recommendations.append(
            f"Estimated monthly cost increase if applied now: ${cost['estimated_monthly_cost_increase']}."
        )

    if (
        cost.get("estimated_monthly_savings", 0) < MIN_SAVINGS_MONTHLY
        and cost.get("estimated_monthly_cost_increase", 0) == 0
        and len(recommendations) == 0
    ):
        recommendations.append(
            "No immediate cost optimization action is recommended; continue monitoring."
        )

    return {
        "workload": WORKLOAD_NAME,
        "recommendations": recommendations,
        "estimated_monthly_savings": cost.get("estimated_monthly_savings", 0.0),
        "estimated_monthly_cost_increase": cost.get("estimated_monthly_cost_increase", 0.0),
        "net_monthly_delta": cost.get("net_monthly_delta", 0.0),
        "rightsizing_basis": {
            "avg_cpu_per_pod_millicores": rightsize["avg_cpu_per_pod_millicores"],
            "avg_memory_per_pod_mib": rightsize["avg_memory_per_pod_mib"],
            "requested_cpu_millicores": rightsize["requested_cpu_millicores"],
            "requested_memory_mib": rightsize["requested_memory_mib"],
        },
    }


@app.get("/patch/resources-preview")
def patch_resources_preview():
    rightsize = get_per_pod_rightsizing(hours=1)

    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [
                        {
                            "name": WORKLOAD_NAME,
                            "resources": {
                                "requests": {
                                    "cpu": f"{rightsize['recommended_cpu_request_millicores']}m",
                                    "memory": f"{rightsize['recommended_memory_request_mib']}Mi",
                                }
                            }
                        }
                    ]
                }
            }
        }
    }

    return {
        "workload": WORKLOAD_NAME,
        "namespace": NAMESPACE,
        "patch": patch,
    }


@app.get("/patch/scaling-preview")
def patch_scaling_preview():
    start, end = get_time_range(hours=1)
    cpu_df = get_cpu_timeseries(start, end, step="5m")
    preds = forecast_next_points(cpu_df, points=FORECAST_POINTS)

    current_cpu = get_current_cpu_millicores()
    current_replicas = get_current_replicas()
    predicted_peak = max(preds) if preds else 0.0
    effective_predicted_cpu = max(predicted_peak, current_cpu)

    scaling = recommend_replicas(effective_predicted_cpu, current_replicas)

    patch = {
        "spec": {
            "replicas": scaling["recommended_replicas"]
        }
    }

    return {
        "workload": WORKLOAD_NAME,
        "namespace": NAMESPACE,
        "current_replicas": current_replicas,
        "recommended_replicas": scaling["recommended_replicas"],
        "action": scaling["action"],
        "patch": patch,
    }
