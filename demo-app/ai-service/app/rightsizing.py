import math
from app.config import CPU_PER_POD_MILLICORES, MEMORY_PER_POD_MIB


def recommend_request(avg_value: float, minimum: int, buffer_ratio: float = 1.3):
    recommended = max(minimum, avg_value * buffer_ratio)

    # round UP to nearest 10, never below minimum
    rounded = int(math.ceil(recommended / 10.0) * 10)
    return max(rounded, minimum)


def get_status(avg_value: float, requested_value: int):
    if avg_value < requested_value * 0.5:
        return "overprovisioned"
    if avg_value > requested_value * 0.9:
        return "underprovisioned"
    return "balanced"


def build_rightsizing(avg_cpu: float, avg_memory: float):
    recommended_cpu = recommend_request(avg_cpu, minimum=50)
    recommended_memory = recommend_request(avg_memory, minimum=64)

    return {
        "avg_cpu_millicores": round(avg_cpu, 2),
        "requested_cpu_millicores": CPU_PER_POD_MILLICORES,
        "recommended_cpu_request_millicores": recommended_cpu,
        "avg_memory_mib": round(avg_memory, 2),
        "requested_memory_mib": MEMORY_PER_POD_MIB,
        "recommended_memory_request_mib": recommended_memory,
        "cpu_status": get_status(avg_cpu, CPU_PER_POD_MILLICORES),
        "memory_status": get_status(avg_memory, MEMORY_PER_POD_MIB)
    }
