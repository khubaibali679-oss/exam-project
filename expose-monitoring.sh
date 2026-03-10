#!/bin/bash

echo "Starting Grafana and Prometheus port forwarding..."

# Grafana (public)
kubectl port-forward --address 0.0.0.0 svc/monitoring-grafana 3000:80 -n monitoring > grafana.log 2>&1 &

GRAFANA_PID=$!

# Prometheus (public)
kubectl port-forward --address 0.0.0.0 svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring > prometheus.log 2>&1 &

PROMETHEUS_PID=$!

echo "Grafana running on: http://YOUR_VM_IP:3000"
echo "Prometheus running on: http://YOUR_VM_IP:9090"

echo "Grafana PID: $GRAFANA_PID"
echo "Prometheus PID: $PROMETHEUS_PID"

echo "Logs:"
echo "  grafana.log"
echo "  prometheus.log"

wait
