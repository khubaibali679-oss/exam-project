import math
from app.config import (
    CPU_PER_POD_MILLICORES,
    MIN_REPLICAS,
    MAX_REPLICAS,
    SCALE_DOWN_CPU_THRESHOLD_M,
)


def recommend_replicas(predicted_cpu_millicores: float, current_replicas: int):
    current_replicas = max(current_replicas, MIN_REPLICAS)

    if predicted_cpu_millicores <= SCALE_DOWN_CPU_THRESHOLD_M:
        return {
            "recommended_replicas": current_replicas,
            "predicted_cpu_per_pod_millicores": round(
                predicted_cpu_millicores / max(current_replicas, 1), 2
            ),
            "action": "keep_current",
            "reason": "Forecasted CPU is too low-confidence for scale-down; keeping current replicas."
        }

    raw_replicas = math.ceil(predicted_cpu_millicores / CPU_PER_POD_MILLICORES)
    recommended = max(MIN_REPLICAS, min(raw_replicas, MAX_REPLICAS))

    # Avoid noisy 1-step oscillation unless clearly needed
    if abs(recommended - current_replicas) == 1:
        current_per_pod = predicted_cpu_millicores / max(current_replicas, 1)
        if current_per_pod < CPU_PER_POD_MILLICORES * 0.85:
            recommended = current_replicas

    if recommended > current_replicas:
        action = "scale_up"
    elif recommended < current_replicas:
        action = "scale_down"
    else:
        action = "keep_current"

    predicted_per_pod = predicted_cpu_millicores / max(recommended, 1)

    return {
        "recommended_replicas": recommended,
        "predicted_cpu_per_pod_millicores": round(predicted_per_pod, 2),
        "action": action,
        "reason": f"Predicted CPU {round(predicted_cpu_millicores, 2)}m evaluated against target {CPU_PER_POD_MILLICORES}m/pod within bounds [{MIN_REPLICAS}, {MAX_REPLICAS}]."
    }
