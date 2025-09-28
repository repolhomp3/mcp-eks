#!/bin/bash

echo "Deploying MCP Servers to EKS..."

# Deploy infrastructure
echo "1. Deploying Terraform infrastructure..."
cd terraform
terraform init
terraform plan
read -p "Apply Terraform changes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply
fi

# Update kubeconfig
echo "2. Updating kubeconfig..."
aws eks update-kubeconfig --region us-west-2 --name mcp-eks-cluster

# Deploy applications
echo "3. Deploying Helm charts..."
cd ../helm
helm install mcp-servers ./mcp-servers

echo "4. Getting service endpoints..."
kubectl get services

echo "Deployment complete!"
echo "Use 'kubectl get pods' to check pod status"
echo "Use 'kubectl get services' to get LoadBalancer URLs"