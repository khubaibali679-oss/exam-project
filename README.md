
# AI Infrastructure Optimizer (Phase 1 MVP)

This project builds a **prototype AI-powered infrastructure optimization platform** running on Kubernetes.  
The system monitors workloads, forecasts demand, and recommends scaling or cost optimizations.

The prototype runs on a **single Azure VM** using **k3s (lightweight Kubernetes)**.

---

# Architecture

```

Azure VM (Ubuntu)
|
├── Docker
├── Kubernetes (k3s – lightweight)
│       ├── Demo App
│       ├── Prometheus
│       ├── Grafana
│       └── Metrics
│
└── AI Optimization Service (FastAPI + ML)
├── Forecast workload
├── Recommend scaling
└── Estimate cost

````

Future enhancements will include:

- Predictive scaling
- Cost optimization
- Anomaly detection
- Multi-cloud simulation

---

# 1️⃣ Azure Infrastructure Setup

Create an **Ubuntu Virtual Machine**.

Recommended configuration:

| Setting | Value |
|------|------|
| VM Type | B2s |
| vCPU | 2 |
| RAM | 4GB |
| Disk | 30GB |
| OS | Ubuntu 22.04 |

Estimated cost: **~$20/month**

---

# 2️⃣ Connect to the VM

```bash
ssh azureuser@YOUR_VM_IP
````

Update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

---

# 3️⃣ Install Core Tools

Create a setup script:

```bash
nano setup.sh
```

Paste:

```bash
#!/bin/bash

echo "Updating system..."
sudo apt update -y

echo "Installing base tools..."
sudo apt install -y \
curl \
wget \
git \
apt-transport-https \
ca-certificates \
software-properties-common \
python3 \
python3-pip \
python3-venv \
jq

echo "Installing Docker..."
curl -fsSL https://get.docker.com | bash

sudo usermod -aG docker $USER

echo "Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

chmod +x kubectl
sudo mv kubectl /usr/local/bin/

echo "Installing Helm..."
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

echo "Installing k3s (lightweight Kubernetes)..."
curl -sfL https://get.k3s.io | sh -

echo "Setting kubeconfig..."
mkdir -p $HOME/.kube
sudo cp /etc/rancher/k3s/k3s.yaml $HOME/.kube/config
sudo chown $USER:$USER $HOME/.kube/config

echo "Testing cluster..."
kubectl get nodes

echo "Setup complete!"
```

Run the script:

```bash
chmod +x setup.sh
./setup.sh
```

Verify cluster:

```bash
kubectl get nodes
```

Expected output:

```
NAME      STATUS   ROLES                  AGE
vm-name   Ready    control-plane,master
```

---

# 4️⃣ Install Prometheus + Grafana

Add Helm repository:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Create monitoring namespace:

```bash
kubectl create namespace monitoring
```

Install monitoring stack:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
--namespace monitoring
```

Check pods:

```bash
kubectl get pods -n monitoring
```

Wait until all pods show **Running**.

---

# 5️⃣ Access Grafana

Get services:

```bash
kubectl get svc -n monitoring
```

Find:

```
monitoring-grafana
```

Port-forward:

```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```

Open browser:

```
http://YOUR_VM_IP:3000
```

Login:

```
username: admin
password: <generated password>
```

Get password:

```bash
kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
```

---

# 6️⃣ Deploy Demo Application

Create folder:

```bash
mkdir demo-app
cd demo-app
```

Create deployment file:

```bash
nano deployment.yaml
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
      - name: demo
        image: nginx
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
```

Apply deployment:

```bash
kubectl apply -f deployment.yaml
```

Check pods:

```bash
kubectl get pods
```

---

# 7️⃣ Add Auto Scaling (HPA)

Create HPA file:

```bash
nano hpa.yaml
```

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo-app
  minReplicas: 2
  maxReplicas: 8
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

Apply HPA:

```bash
kubectl apply -f hpa.yaml
```

Check HPA:

```bash
kubectl get hpa
```

---

# 8️⃣ Install Metrics Server

Required for HPA.

Install:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

Edit deployment:

```bash
kubectl edit deployment metrics-server -n kube-system
```

Add argument:

```
--kubelet-insecure-tls
```

Verify metrics:

```bash
kubectl top nodes
```

---

# 9️⃣ Create AI Optimization Service

Create folder:

```bash
mkdir ai-service
cd ai-service
```

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install fastapi uvicorn pandas scikit-learn requests prophet
```

---

# 🔟 AI Service Code

Create file:

```bash
nano main.py
```

```python
from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Infrastructure Optimizer Running"}

@app.get("/forecast")
def forecast():
    predicted_cpu = random.randint(30, 90)

    return {
        "predicted_cpu_usage": predicted_cpu,
        "recommended_action":
            "scale_up" if predicted_cpu > 70 else "scale_down"
    }

@app.get("/cost-estimate")
def cost():

    aws_cost = 0.24
    azure_cost = 0.21

    return {
        "aws_hourly_cost": aws_cost,
        "azure_hourly_cost": azure_cost,
        "recommended_cloud":
            "azure" if azure_cost < aws_cost else "aws"
    }
```

Run service:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open API docs:

```
http://YOUR_VM_IP:8000/docs
```

---

# 1️⃣1️⃣ Example API Output

Forecast endpoint:

```
GET /forecast
```

Example response:

```json
{
 "predicted_cpu_usage": 82,
 "recommended_action": "scale_up"
}
```

Cost estimate endpoint:

```
GET /cost-estimate
```

Example response:

```json
{
 "aws_hourly_cost": 0.24,
 "azure_hourly_cost": 0.21,
 "recommended_cloud": "azure"
}
```

---

# 1️⃣2️⃣ Connect AI Service with Kubernetes (Future)

Next phase will allow the AI service to:

* Read metrics from **Prometheus API**
* Predict workload trends
* Recommend scaling decisions
* Automatically update HPA

Example scaling command:

```bash
kubectl scale deployment demo-app --replicas=5
```

---

# 1️⃣3️⃣ Current MVP Features

Working platform:

```
Azure VM
   |
   ├── Kubernetes (k3s)
   │       ├── Demo App
   │       ├── HPA autoscaling
   │       └── Metrics Server
   │
   ├── Prometheus
   ├── Grafana dashboards
   │
   └── AI Optimization API
           ├── Forecast load
           ├── Recommend scaling
           └── Compare cloud cost
```

This prototype already demonstrates:

* Predictive scaling concepts
* Performance monitoring
* Cost optimization insights
* Infrastructure automation



