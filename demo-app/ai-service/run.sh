#!/bin/bash
export PROMETHEUS_URL="http://localhost:9090"
export WORKLOAD_NAME="demo-app"
export NAMESPACE="default"
export NODE_TYPE="B2s"
export TARGET_CPU_UTILIZATION="60"
export CPU_PER_POD_MILLICORES="200"
export MEMORY_PER_POD_MIB="128"
export MIN_REPLICAS="2"
export MAX_REPLICAS="8"
export FORECAST_POINTS="6"
export SCALE_DOWN_CPU_THRESHOLD_M="50"
export MIN_SAVINGS_MONTHLY="1.0"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
