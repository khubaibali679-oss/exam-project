import json
from pathlib import Path
from app.config import NODE_TYPE


PRICING_FILE = Path("pricing/azure_vm_pricing.json")


def load_pricing():
    with open(PRICING_FILE, "r") as f:
        return json.load(f)


def get_node_hourly_cost():
    pricing = load_pricing()
    return pricing.get(NODE_TYPE, {}).get("hourly", 0.05)


def estimate_workload_cost(current_replicas: int, recommended_replicas: int):
    node_hourly_cost = get_node_hourly_cost()

    # Simple prototype assumption:
    # each pod is treated as an equal share of node capacity.
    # We assume 10 pods roughly fit a node for demo purposes.
    cost_per_pod_hour = node_hourly_cost / 10

    current_hourly = current_replicas * cost_per_pod_hour
    optimized_hourly = recommended_replicas * cost_per_pod_hour

    return {
        "current_hourly_cost": round(current_hourly, 4),
        "current_daily_cost": round(current_hourly * 24, 4),
        "current_monthly_cost": round(current_hourly * 24 * 30, 4),
        "optimized_hourly_cost": round(optimized_hourly, 4),
        "optimized_daily_cost": round(optimized_hourly * 24, 4),
        "optimized_monthly_cost": round(optimized_hourly * 24 * 30, 4),
        "estimated_monthly_savings": round((current_hourly - optimized_hourly) * 24 * 30, 4)
    }
