# AI-Driven Kubernetes Infrastructure Optimization

An intelligent Kubernetes infrastructure optimization prototype that combines monitoring, predictive scaling, rightsizing, cost estimation, and patch preview generation for cloud-native workloads.

---

## 1. Introduction

This project is a working prototype of an **AI-driven infrastructure optimization platform** built for Kubernetes workloads.

The system continuously:

- Collects infrastructure metrics from Prometheus
- Analyzes current workload behavior
- Predicts near-future CPU demand
- Recommends horizontal scaling actions
- Recommends CPU and memory rightsizing
- Estimates cost impact
- Generates Kubernetes patch previews for resource and scaling changes

The current demo uses a synthetic workload called **`demo-burst`** that generates controlled random CPU and memory usage so the optimizer can observe changing behavior and produce recommendations.

This project demonstrates the core ideas behind:

- Predictive scaling
- Capacity planning
- FinOps-inspired cost awareness
- Automated infrastructure optimization
- Intelligent Kubernetes operations

---

## 2. Project Goals

1. Monitor Kubernetes workloads in real time
2. Predict short-term resource demand
3. Recommend better replica counts
4. Detect whether CPU and memory requests are too high or too low
5. Estimate the cost impact of scaling decisions
6. Produce ready-to-apply Kubernetes patch previews

---

## 3. Current Features

### Implemented Features

- Kubernetes-based demo environment
- Prometheus and Grafana monitoring stack
- FastAPI optimization service
- CPU forecasting
- Replica recommendation engine
- Rightsizing analysis
- Cost estimation
- Patch preview endpoints
- Capacity warning detection

### Current Active Workload

- `demo-burst`
- Kubernetes Deployment + HPA
- Random stress workload with safe resource limits

---

## 4. High-Level Architecture

```text
                         ┌─────────────────────────────┐
                         │        Kubernetes Cluster    │
                         │                             │
                         │  demo-burst Deployment      │
                         │  demo-burst HPA             │
                         └──────────────┬──────────────┘
                                        │
                                        │ metrics
                                        ▼
                         ┌─────────────────────────────┐
                         │         Prometheus           │
                         │  Collects workload metrics   │
                         └──────────────┬──────────────┘
                                        │
                                        │ API queries
                                        ▼
                    ┌─────────────────────────────────────────┐
                    │     AI Optimization Service (FastAPI)   │
                    │                                         │
                    │  - current metrics                      │
                    │  - workload forecasting                 │
                    │  - scaling recommendations              │
                    │  - rightsizing analysis                 │
                    │  - cost estimation                      │
                    │  - patch preview generation             │
                    └──────────────┬──────────────────────────┘
                                   │
                                   │ API responses
                                   ▼
                    ┌─────────────────────────────────────────┐
                    │     User / DevOps Engineer / Dashboard  │
                    │                                         │
                    │  - view recommendations                 │
                    │  - review cost impact                   │
                    │  - apply generated patches manually     │
                    └─────────────────────────────────────────┘
```

---

## 5. Project Flow

```text
demo-burst generates load
        ↓
Prometheus collects CPU, memory, replicas
        ↓
FastAPI service queries Prometheus
        ↓
System calculates current state
        ↓
Forecasting predicts future CPU demand
        ↓
Scaling engine computes ideal replicas
        ↓
Rightsizing engine computes ideal CPU/memory requests
        ↓
Cost model estimates financial impact
        ↓
Patch preview endpoints generate Kubernetes patch objects
```

---

## 6. Repository Structure

```text
project/
├── README.md
├── ai-service/
│   ├── app/
│   │   ├── config.py
│   │   ├── cost_model.py
│   │   ├── forecasting.py
│   │   ├── main.py
│   │   ├── prometheus_client.py
│   │   ├── rightsizing.py
│   │   ├── scaling.py
│   │   └── schemas.py
│   ├── pricing/
│   │   └── azure_vm_pricing.json
│   ├── requirements.txt
│   └── run.sh
├── manifests/
│   └── demo-burst.yaml
├── expose-monitoring.sh
├── setup.sh
└── archive/
```

---

## 7. Component Explanation

### 7.1 Kubernetes Workload

The active demo workload is:

- **Deployment:** `demo-burst`
- **HPA:** `demo-burst-hpa`

This workload uses `alpine + stress-ng` to generate variable CPU and memory load. Its purpose is to simulate a changing workload so the optimization engine has real data to analyze.

### 7.2 Prometheus

Prometheus collects:

- Container CPU usage
- Container memory usage
- Deployment replica count

The optimization service queries Prometheus to retrieve both current metrics and time-series history.

### 7.3 AI Optimization Service

The FastAPI service is the main logic layer. It contains:

- Metric ingestion logic
- Simple forecasting logic
- Scaling recommendation logic
- Rightsizing logic
- Cost model
- Patch preview generation

### 7.4 Forecasting Engine

The forecasting engine uses recent Prometheus CPU data to predict short-term future CPU demand.

**Current prototype behavior:**

- Forecast horizon: 30 minutes
- Interval-based CPU prediction
- Stable bounded forecasting logic for demo reliability

### 7.5 Scaling Engine

The scaling engine calculates recommended replicas using:

```text
recommended_replicas = ceil(predicted_cpu / cpu_per_pod_target)
```

Then it applies:

- Minimum replica bound
- Maximum replica bound
- Action classification: `scale_up`, `scale_down`, `keep_current`

### 7.6 Rightsizing Engine

The rightsizing engine compares average CPU and memory per pod against configured CPU and memory requests per pod, then classifies each resource as:

- `underprovisioned`
- `balanced`
- `overprovisioned`

And calculates a buffered recommendation.

### 7.7 Cost Model

The cost model estimates the cost impact of scaling changes using a simplified pricing model. It computes:

- Current hourly, daily, monthly cost
- Optimized cost
- Monthly savings / cost increase
- Net monthly delta

This is a simplified prototype FinOps layer.

### 7.8 Patch Preview Engine

The system generates Kubernetes patch previews **without auto-applying them**. Two main patch types are supported:

- Resource request patch preview
- Replica scaling patch preview

This makes the system safer because engineers can review recommendations before applying them.

---

## 8. API Endpoints

### 8.1 `GET /`

Basic health/root endpoint.

```json
{
  "message": "AI Infrastructure Optimizer Running"
}
```

### 8.2 `GET /metrics/current`

Returns the current state of the monitored workload, including workload name, namespace, total CPU/memory usage, and replica count.

```json
{
  "workload": "demo-burst",
  "namespace": "default",
  "current_cpu_millicores": 849.17,
  "current_memory_mib": 103.84,
  "current_replicas": 4
}
```

### 8.3 `GET /forecast`

Predicts near-future CPU demand. Enables predictive scaling instead of purely reactive scaling.

```json
{
  "workload": "demo-burst",
  "forecast_points": [849.08, 849.08, 849.08, 849.08, 849.08, 849.08],
  "unit": "millicores",
  "horizon_minutes": 30,
  "lookback_hours": 1
}
```

### 8.4 `GET /recommendations`

Returns scaling recommendations including current replicas, predicted CPU, recommended replicas, action, reason, and any capacity warnings.

```json
{
  "workload": "demo-burst",
  "current_replicas": 4,
  "predicted_cpu_millicores": 848.92,
  "predicted_cpu_per_pod_millicores": 169.78,
  "recommended_replicas": 5,
  "action": "scale_up",
  "reason": "Predicted CPU 848.92m evaluated against target 120m/pod within bounds [2, 5].",
  "capacity_warning": "Predicted CPU 848.92m exceeds modeled max capacity 600m at MAX_REPLICAS=5."
}
```

### 8.5 `GET /scaling/explain`

Provides a detailed explanation of how the scaling decision was made — useful for debugging, verification, and operator transparency.

### 8.6 `GET /rightsizing`

Analyzes CPU and memory requests per pod and returns current averages, recommended requests, and status classifications.

```json
{
  "workload": "demo-burst",
  "lookback_hours": 1,
  "current_replicas": 4,
  "avg_cpu_total_millicores": 511.71,
  "avg_memory_total_mib": 127.99,
  "avg_cpu_per_pod_millicores": 127.93,
  "avg_memory_per_pod_mib": 32.0,
  "avg_cpu_millicores": 127.93,
  "requested_cpu_millicores": 120,
  "recommended_cpu_request_millicores": 170,
  "avg_memory_mib": 32.0,
  "requested_memory_mib": 96,
  "recommended_memory_request_mib": 70,
  "cpu_status": "underprovisioned",
  "memory_status": "overprovisioned"
}
```

### 8.7 `GET /cost/summary`

Returns summarized cost estimates including current cost, optimized cost, monthly savings, and net monthly delta.

### 8.8 `GET /cost/recommendations`

Returns human-readable optimization recommendations with cost implications.

```json
{
  "workload": "demo-burst",
  "recommendations": [
    "Increase CPU request from 120m to 170m.",
    "Lower memory request from 96Mi to 70Mi."
  ],
  "estimated_monthly_savings": 0.0,
  "estimated_monthly_cost_increase": 0.0,
  "net_monthly_delta": 0.0,
  "rightsizing_basis": {
    "avg_cpu_per_pod_millicores": 127.94,
    "avg_memory_per_pod_mib": 32.0,
    "requested_cpu_millicores": 120,
    "requested_memory_mib": 96
  }
}
```

### 8.9 `GET /patch/resources-preview`

Generates a Kubernetes patch preview for resource request changes.

```json
{
  "workload": "demo-burst",
  "namespace": "default",
  "patch": {
    "spec": {
      "template": {
        "spec": {
          "containers": [
            {
              "name": "demo-burst",
              "resources": {
                "requests": {
                  "cpu": "170m",
                  "memory": "70Mi"
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

### 8.10 `GET /patch/scaling-preview`

Generates a Kubernetes patch preview for replica changes.

```json
{
  "workload": "demo-burst",
  "namespace": "default",
  "current_replicas": 4,
  "recommended_replicas": 4,
  "action": "keep_current",
  "patch": {
    "spec": {
      "replicas": 4
    }
  }
}
```

---

## 9. How the Optimization Logic Works

### 9.1 Current Metrics
The service reads current total CPU, memory, and replica count.

### 9.2 Forecast
Reads recent CPU history from Prometheus and predicts near-future CPU demand.

### 9.3 Scaling Recommendation
Calculates ideal replicas based on predicted CPU, applies min/max bounds, and returns action type with capacity warning if relevant.

### 9.4 Rightsizing
Calculates average CPU and memory per pod, compares against configured requests, and recommends better values.

### 9.5 Cost Impact
Estimates the financial effect of scaling changes.

### 9.6 Patch Preview
Generates Kubernetes patch objects for manual review and future automation.

---

## 10. Demo Workload Explanation

The active demo workload is `demo-burst`. It is a stress workload that:

- Randomly consumes CPU
- Randomly allocates memory
- Sleeps between bursts
- Stays within Kubernetes resource limits

This makes it useful for testing monitoring, forecasting, rightsizing logic, and demonstrating optimization behavior.

---

## 11. Resource Safety

The demo workload is intentionally limited so it does not consume the entire VM.

```yaml
resources:
  requests:
    cpu: "80m"
    memory: "64Mi"
  limits:
    cpu: "200m"
    memory: "128Mi"
```

---

## 12. Setup Overview

### 12.1 Infrastructure Setup

Use `setup.sh` to install Docker, kubectl, Helm, and k3s.

### 12.2 Monitoring Exposure

Use `expose-monitoring.sh` to expose Grafana and Prometheus.

### 12.3 Workload Deployment

```bash
kubectl apply -f ~/project/manifests/demo-burst.yaml
```

### 12.4 Start API

```bash
cd ~/project/ai-service
./run.sh
```

---

## 13. Verification Commands

### Kubernetes Checks

```bash
kubectl get deploy -A
kubectl get hpa -A
kubectl get pods -A -o wide
kubectl top pods
kubectl top nodes
```

### API Checks

```bash
curl http://localhost:8000/metrics/current
curl http://localhost:8000/forecast
curl http://localhost:8000/recommendations
curl http://localhost:8000/scaling/explain
curl http://localhost:8000/rightsizing
curl http://localhost:8000/cost/summary
curl http://localhost:8000/cost/recommendations
curl http://localhost:8000/patch/resources-preview
curl http://localhost:8000/patch/scaling-preview
```

---

## 14. Debugging Guide

### 14.1 API Not Starting

```bash
cd ~/project/ai-service
./run.sh
# If it fails, reinstall dependencies:
pip install -r requirements.txt
```

### 14.2 Prometheus Data Missing

```bash
curl http://localhost:9090/-/healthy
```

If Prometheus is not forwarded, start the exposure script again and verify Prometheus queries inside the service.

### 14.3 Workload Not Found

```bash
kubectl get deploy
kubectl get pods -l app=demo-burst
# Re-apply manifest if needed:
kubectl apply -f ~/project/manifests/demo-burst.yaml
```

### 14.4 HPA Missing or Not Scaling

```bash
kubectl get hpa
kubectl describe hpa demo-burst-hpa
kubectl top pods
```

If CPU metrics are missing, check metrics-server and pod resource requests/limits.

### 14.5 Wrong Scaling Recommendations

**Possible causes:** incorrect `CPU_PER_POD_MILLICORES`, stale metrics, max replicas too low, or workload demand exceeding modeled capacity.

**Fix:** Adjust `run.sh` and restart the API.

### 14.6 Capacity Warning Appears

**Meaning:** Predicted demand is higher than modeled cluster capacity under the current max replica constraint.

**Typical fixes:**
- Increase `MAX_REPLICAS`
- Increase pod CPU target
- Reduce workload intensity
- Add more node capacity

---

## 15. Current Status

### Confirmed Working

- Monitoring stack
- Kubernetes workload deployment
- Current metric retrieval
- Forecasting
- Scaling recommendation
- Rightsizing
- Cost recommendation
- Patch preview generation

### Current Operating Mode

- Recommendation mode
- Preview mode
- **No automatic patch application**

---

## 16. Limitations

- Cost model is approximate
- Resource requests are based on configured values, not yet pulled live from Kubernetes spec
- Forecasting is simplified
- Recommendations are not auto-applied
- Only one main demo workload is actively optimized at a time

---

## 17. Future Improvements

- Read actual resource requests and limits directly from Kubernetes
- Add anomaly detection
- Add workload selection via query parameter
- Add automatic patch application mode
- Add richer forecasting models
- Add SLA and latency analysis
- Add multi-cloud placement comparison
- Add Grafana panels for optimizer endpoints

---

## 18. Summary

This prototype monitors a Kubernetes workload, predicts its future CPU demand, checks whether the current number of pods is sufficient, checks whether CPU and memory requests are well-sized, estimates cost impact, and generates Kubernetes patch previews so engineers can optimize the system safely.

> **In short:** An AI-assisted Kubernetes optimizer that turns monitoring data into scaling and resource recommendations.

---

## 19. Example End-to-End Story

1. `demo-burst` generates random load
2. Prometheus collects CPU, memory, and replica metrics
3. FastAPI reads those metrics
4. Forecasting predicts short-term CPU demand
5. The scaling engine decides whether to increase, decrease, or keep replicas
6. The rightsizing engine checks whether CPU and memory requests are too high or too low
7. The cost model estimates impact
8. Patch preview endpoints generate Kubernetes patch objects
9. An engineer reviews and applies the recommendation manually

---

## 20. Conclusion

This prototype demonstrates a practical foundation for intelligent infrastructure optimization. It combines:

- **Observability** — real-time metric collection via Prometheus
- **Predictive analysis** — CPU forecasting for proactive scaling
- **Infrastructure tuning** — rightsizing CPU and memory requests
- **Cost awareness** — FinOps-inspired cost estimation
- **Automation readiness** — patch preview generation for safe human-in-the-loop workflows

Although still a prototype, it already behaves like a real optimization assistant for Kubernetes workloads and can be extended into a more advanced production-grade platform.
