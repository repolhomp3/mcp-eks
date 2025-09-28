# MCP-EKS Architecture Description

## System Overview
A production-ready Model Context Protocol (MCP) server deployment on Amazon EKS, demonstrating secure AI integration patterns with enterprise-grade infrastructure automation.

## High-Level Architecture

### Regional Layout
- **AWS Region**: us-west-2 (Oregon)
- **Availability Zones**: 3 AZs for high availability
- **Network**: Custom VPC with public/private subnet architecture

### Core Infrastructure Components

#### 1. Amazon VPC Network Architecture
```
VPC (10.0.0.0/16)
├── Public Subnets (3 AZs)
│   ├── 10.0.4.0/20 (us-west-2a)
│   ├── 10.0.5.0/20 (us-west-2b) 
│   └── 10.0.6.0/20 (us-west-2c)
├── Private Subnets (3 AZs)
│   ├── 10.0.0.0/20 (us-west-2a)
│   ├── 10.0.1.0/20 (us-west-2b)
│   └── 10.0.2.0/20 (us-west-2c)
├── Internet Gateway
├── NAT Gateway (public subnet)
└── Route Tables (public/private)
```

#### 2. Amazon EKS Cluster
- **Control Plane**: Managed EKS 1.33 in private subnets
- **Worker Nodes**: Managed node groups + Karpenter-provisioned nodes
- **Networking**: VPC-CNI for pod networking
- **Storage**: EBS CSI driver for persistent volumes
- **DNS**: CoreDNS for service discovery
- **Proxy**: kube-proxy for service networking

#### 3. Node Management & Autoscaling
- **Initial Nodes**: 2x t3.medium managed node group
- **Karpenter**: Intelligent node provisioning (t3.medium to t3.xlarge)
- **KEDA**: Event-driven horizontal pod autoscaling
- **Instance Types**: Spot and on-demand mix for cost optimization

### Application Layer

#### 4. MCP Server Deployments
Four containerized MCP servers, each with:
- **Deployment**: Kubernetes deployment with 1+ replicas
- **Service**: LoadBalancer type for external access
- **HPA**: CPU-based autoscaling (1-10 replicas)
- **Health Checks**: Liveness and readiness probes
- **Resources**: CPU/memory limits and requests

#### 5. MCP Server Types & Functions

**AWS MCP Server**
- **Purpose**: AWS service integration
- **Capabilities**: Bedrock AI, S3 operations, region discovery
- **Security**: Pod Identity for AWS API access
- **External Dependencies**: Amazon Bedrock, S3, EC2 APIs

**Database MCP Server**
- **Purpose**: Database operations
- **Capabilities**: SQLite queries, schema introspection
- **Storage**: Embedded SQLite database in container
- **Sample Data**: Users and projects tables

**Custom MCP Server**
- **Purpose**: External API integration template
- **Capabilities**: Weather API, key-value storage, timestamps
- **External Dependencies**: wttr.in weather API
- **State**: In-memory data store

**Filesystem MCP Server**
- **Purpose**: Secure file system access
- **Capabilities**: Directory listing, file operations
- **Security**: Path restrictions for container safety
- **Scope**: Container filesystem access only

#### 6. Frontend Dashboard
- **Technology**: Static HTML/CSS/JavaScript
- **Hosting**: Nginx container
- **Purpose**: Interactive demo interface
- **Connectivity**: HTTP calls to MCP server LoadBalancers

### Security & Identity

#### 7. AWS IAM & Pod Identity
- **Pod Identity Agent**: EKS addon for secure AWS access
- **IAM Role**: `mcp-pod-role` with specific AWS permissions
- **Service Account**: `mcp-service-account` linked to IAM role
- **Permissions**: Bedrock, S3, EC2 describe operations
- **Scope**: Only AWS MCP server uses Pod Identity

#### 8. Network Security
- **Subnet Isolation**: Private subnets for worker nodes
- **Security Groups**: EKS-managed security groups
- **LoadBalancer**: AWS ALB for external traffic
- **Ingress**: Internet → ALB → Kubernetes Services → Pods

### Infrastructure as Code

#### 9. Terraform Infrastructure
- **VPC Module**: terraform-aws-modules/vpc
- **EKS Module**: terraform-aws-modules/eks  
- **Karpenter Module**: terraform-aws-modules/eks//modules/karpenter
- **Addons**: VPC-CNI, EBS-CSI, CoreDNS, kube-proxy, Pod Identity
- **State**: Local state (can be moved to S3 backend)

#### 10. Helm Application Deployment
- **Chart Structure**: Single chart with multiple deployments
- **Templates**: Separate YAML per MCP server type
- **Values**: Centralized configuration in values.yaml
- **Features**: Conditional deployment, resource templating

### Data Flow & Communication

#### 11. External User Interaction
```
User Browser → ALB LoadBalancer → Frontend Service → Frontend Pod
Frontend JavaScript → ALB LoadBalancers → MCP Services → MCP Pods
```

#### 12. MCP Server Communication Patterns
```
AWS MCP Pod → Pod Identity → AWS APIs (Bedrock/S3/EC2)
Database MCP Pod → Local SQLite file
Custom MCP Pod → External Weather API (wttr.in)
Filesystem MCP Pod → Container filesystem
```

#### 13. Kubernetes Internal Communication
```
kubectl/Helm → EKS API Server → kubelet → Pods
Karpenter → AWS EC2 API → Node provisioning
KEDA → Metrics Server → HPA → Pod scaling
```

### Monitoring & Observability

#### 14. Built-in Monitoring
- **Health Probes**: HTTP endpoints (/health, /ready)
- **Resource Metrics**: CPU/memory via metrics-server
- **Kubernetes Events**: Pod lifecycle, scaling events
- **AWS CloudTrail**: API call auditing

#### 15. Scaling Behavior
- **Pod Scaling**: KEDA HPA based on CPU utilization (80% threshold)
- **Node Scaling**: Karpenter provisions nodes based on pod resource requests
- **Cost Optimization**: Spot instances, right-sizing, automatic scale-down

### Deployment Pipeline

#### 16. Build Process
```
Source Code → Docker Build → Container Registry → Helm Deploy
├── MCP Servers (Python)
├── Frontend (HTML/JS)
└── Infrastructure (Terraform)
```

#### 17. Container Registry Options
- **Amazon ECR**: Recommended for AWS integration
- **Docker Hub**: Alternative public registry
- **Image Tags**: Configurable (default: latest)

### Cost Structure

#### 18. Cost Components (2-hour demo)
- **EKS Control Plane**: $0.10/hour
- **EC2 Instances**: 2x t3.medium = $0.0832/hour
- **LoadBalancers**: 5x ALB = ~$0.01/hour
- **Data Transfer**: Minimal for demo
- **Total**: ~$0.39 for 2 hours

### Production Considerations

#### 19. Security Enhancements
- Replace wildcard IAM permissions with resource-specific ARNs
- Implement Kubernetes Network Policies
- Enable EKS audit logging
- Use specific container image tags
- Add secrets management (AWS Secrets Manager)

#### 20. Scalability & Reliability
- Multi-region deployment
- Database persistence (RDS/DynamoDB)
- Circuit breakers for external APIs
- Distributed tracing and logging
- Backup and disaster recovery procedures

This architecture demonstrates modern cloud-native patterns including infrastructure as code, container orchestration, intelligent autoscaling, and secure service-to-service communication in a production-ready AWS environment.