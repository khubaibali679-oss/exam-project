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
