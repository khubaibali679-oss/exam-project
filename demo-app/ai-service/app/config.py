import os

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
WORKLOAD_NAME = os.getenv("WORKLOAD_NAME", "demo-app")
NAMESPACE = os.getenv("NAMESPACE", "default")

NODE_TYPE = os.getenv("NODE_TYPE", "B2s")
TARGET_CPU_UTILIZATION = float(os.getenv("TARGET_CPU_UTILIZATION", "60"))
CPU_PER_POD_MILLICORES = int(os.getenv("CPU_PER_POD_MILLICORES", "200"))
MEMORY_PER_POD_MIB = int(os.getenv("MEMORY_PER_POD_MIB", "128"))

MIN_REPLICAS = int(os.getenv("MIN_REPLICAS", "2"))
MAX_REPLICAS = int(os.getenv("MAX_REPLICAS", "8"))

FORECAST_POINTS = int(os.getenv("FORECAST_POINTS", "6"))
SCALE_DOWN_CPU_THRESHOLD_M = float(os.getenv("SCALE_DOWN_CPU_THRESHOLD_M", "50"))
MIN_SAVINGS_MONTHLY = float(os.getenv("MIN_SAVINGS_MONTHLY", "1.0"))
