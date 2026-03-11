#!/bin/bash
export PROMETHEUS_URL="http://localhost:9090"
export WORKLOAD_NAME="demo-burst"
export NAMESPACE="default"
export NODE_TYPE="B2s"

# Match your demo-burst workload
export CPU_PER_POD_MILLICORES="120"
export MEMORY_PER_POD_MIB="96"

export TARGET_CPU_UTILIZATION="60"
export MIN_REPLICAS="2"
export MAX_REPLICAS="5"
export FORECAST_POINTS="6"
export SCALE_DOWN_CPU_THRESHOLD_M="50"
export MIN_SAVINGS_MONTHLY="1.0"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
