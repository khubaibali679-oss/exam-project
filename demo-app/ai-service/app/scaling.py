import math
from app.config import (
    CPU_PER_POD_MILLICORES,
    MIN_REPLICAS,
    MAX_REPLICAS,
    SCALE_DOWN_CPU_THRESHOLD_M,
)


def recommend_replicas(predicted_cpu_millicores: float, current_replicas: int):
    if current_replicas < 1:
        current_replicas = MIN_REPLICAS

    # If forecast is too small / weak, don't aggressively shrink below min replicas
    if predicted_cpu_millicores <= SCALE_DOWN_CPU_THRESHOLD_M:
        return {
            "recommended_replicas": max(current_replicas, MIN_REPLICAS),
            "predicted_cpu_per_pod_millicores": round(
                predicted_cpu_millicores / max(current_replicas, 1), 2
            ),
            "action": "keep_current",
            "reason": "Forecasted CPU is very low; keeping current replicas to avoid unnecessary scale-down."
        }

    recommended = math.ceil(predicted_cpu_millicores / CPU_PER_POD_MILLICORES)
    recommended = max(MIN_REPLICAS, recommended)
    recommended = min(MAX_REPLICAS, recommended)

    if recommended > current_replicas:
        action = "scale_up"
    elif recommended < current_replicas:
        action = "scale_down"
    else:
        action = "keep_current"

    predicted_per_pod = predicted_cpu_millicores / recommended if recommended else predicted_cpu_millicores

    return {
        "recommended_replicas": recommended,
        "predicted_cpu_per_pod_millicores": round(predicted_per_pod, 2),
        "action": action,
        "reason": f"Predicted CPU {round(predicted_cpu_millicores, 2)}m mapped to replica bounds [{MIN_REPLICAS}, {MAX_REPLICAS}]."
    }
