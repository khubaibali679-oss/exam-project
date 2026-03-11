#!/bin/bash
set -e

echo "Creating demo-burst.yaml..."
cat > demo-burst.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-burst
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo-burst
  template:
    metadata:
      labels:
        app: demo-burst
    spec:
      containers:
        - name: demo-burst
          image: alpine:3.19
          command: ["/bin/sh", "-c"]
          args:
            - |
              set -e
              apk add --no-cache stress-ng bash coreutils
              echo "demo-burst started"

              while true; do
                CPU_WORKERS=$(( (RANDOM % 2) + 1 ))
                MEM_MB=$(( (RANDOM % 70) + 30 ))
                DURATION=$(( (RANDOM % 25) + 10 ))
                SLEEP_GAP=$(( (RANDOM % 20) + 5 ))

                echo "Burst: cpu=${CPU_WORKERS}, mem=${MEM_MB}MB, duration=${DURATION}s, sleep=${SLEEP_GAP}s"

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
              cpu: "120m"
              memory: "96Mi"
            limits:
              cpu: "350m"
              memory: "192Mi"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-burst-hpa
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-burst
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

echo "Applying demo-burst.yaml..."
kubectl apply -f demo-burst.yaml

echo "Waiting for pods..."
sleep 5

echo "Pods:"
kubectl get pods -o wide

echo "HPA:"
kubectl get hpa

echo "Top pods:"
kubectl top pods || true

echo "Done."
