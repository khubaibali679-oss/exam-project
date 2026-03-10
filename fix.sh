#!/bin/bash
set -e

echo "Deleting old deployments if they exist..."
kubectl delete deployment demo-app --ignore-not-found
kubectl delete deployment random-stress --ignore-not-found

echo "Creating demo-app-stress.yaml..."
cat > demo-app-stress.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-app
  template:
    metadata:
      labels:
        app: demo-app
    spec:
      containers:
        - name: demo-app
          image: alpine:3.19
          command: ["/bin/sh", "-c"]
          args:
            - |
              set -e
              apk add --no-cache stress-ng bash coreutils
              echo "demo-app stress workload started"
              while true; do
                CPU_WORKERS=$(( (RANDOM % 2) + 1 ))
                MEM_MB=$(( (RANDOM % 80) + 40 ))
                DURATION=$(( (RANDOM % 20) + 15 ))
                SLEEP_GAP=$(( (RANDOM % 15) + 10 ))

                echo "cpu=${CPU_WORKERS}, mem=${MEM_MB}MB, duration=${DURATION}s, sleep=${SLEEP_GAP}s"
                stress-ng \
                  --cpu ${CPU_WORKERS} \
                  --vm 1 \
                  --vm-bytes ${MEM_MB}M \
                  --timeout ${DURATION}s \
                  --metrics-brief || true

                sleep ${SLEEP_GAP}
              done
          resources:
            requests:
              cpu: "150m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-app-hpa
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-app
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
EOF

echo "Applying demo-app-stress.yaml..."
kubectl apply -f demo-app-stress.yaml

echo "Waiting for pods..."
sleep 5

echo "Current pods:"
kubectl get pods

echo "Current HPA:"
kubectl get hpa

echo "Top pods:"
kubectl top pods || true

echo "Done."
