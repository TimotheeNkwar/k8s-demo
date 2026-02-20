# FastAPI on Kubernetes: Complete Tutorial 🚀

A comprehensive guide to containerizing and deploying a FastAPI application on Kubernetes using Minikube. This tutorial covers Docker fundamentals, Kubernetes concepts, and best practices for production-ready applications.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Core Concepts](#core-concepts)
4. [Part 1: Docker Fundamentals](#part-1-docker-fundamentals)
5. [Part 2: Kubernetes Basics](#part-2-kubernetes-basics)
6. [Part 3: Deployment Guide](#part-3-deployment-guide)
7. [Part 4: Advanced Topics](#part-4-advanced-topics)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting this tutorial, ensure you have the following installed:

- **Docker**: [Installation Guide](https://docs.docker.com/get-docker/)
- **Minikube**: [Installation Guide](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: [Installation Guide](https://kubernetes.io/docs/tasks/tools/)
- **Python 3.11+**: For local development

### Verify Installations

```bash
# Check Docker
docker --version

# Check Minikube
minikube version

# Check kubectl
kubectl version --client
```

---

## Project Structure

```
k8s-demo/
├── app.py                  # FastAPI application (main logic)
├── Dockerfile              # Docker image configuration
├── deployment.yaml         # Kubernetes Deployment manifest
├── service.yaml            # Kubernetes Service manifest
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration (Poetry)
└── README.md              # This file
```

### File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Contains your FastAPI application with routes and endpoints |
| `Dockerfile` | Defines how to build a Docker image from your code |
| `deployment.yaml` | Tells Kubernetes how to run your application (replicas, resources, etc.) |
| `service.yaml` | Exposes your application to external traffic |
| `requirements.txt` | Lists all Python package dependencies |

---

## Core Concepts

### What is Docker?

**Docker** is a containerization platform that packages your application and all its dependencies into a standardized unit called a **container**. Think of it as a lightweight virtual machine.

**Benefits:**

- ✅ Consistency: Runs the same everywhere (dev, staging, production)
- ✅ Isolation: Packages are isolated from each other
- ✅ Efficiency: Minimal overhead compared to VMs

### What is Kubernetes?

**Kubernetes** (K8s) is an orchestration platform that automates deployment, scaling, and management of containerized applications. It handles:

- **Container Scheduling**: Decides which node runs which container
- **Load Balancing**: Distributes traffic across containers
- **Self-Healing**: Restarts failed containers automatically
- **Rolling Updates**: Updates applications without downtime

### What is Minikube?

**Minikube** is a lightweight Kubernetes cluster that runs locally on your machine. It's perfect for development and learning, simulating a production Kubernetes environment without the complexity or cost.

---

## Part 1: Docker Fundamentals

### Understanding the Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Upgrade pip and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Switch to non-root user
USER appuser

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Breaking Down Each Line

| Instruction | Explanation | Why It Matters |
|------------|-------------|----------------|
| `FROM python:3.11-slim` | Starts from an official Python 3.11 image | Slim variant is smaller (~180MB vs 900MB) |
| `WORKDIR /app` | Sets the container's working directory | Makes file paths cleaner and more predictable |
| `RUN useradd -m -u 1000 appuser` | Creates a non-root user | **Security**: Prevents privilege escalation attacks |
| `COPY requirements.txt .` | Copies dependencies file into container | Must install before copying code (layer caching) |
| `RUN pip install --upgrade pip` | Updates pip to latest version | Avoids deprecation warnings |
| `RUN pip install --no-cache-dir -r requirements.txt` | Installs Python dependencies | `--no-cache-dir` reduces image size |
| `COPY app.py .` | Copies application code into container | Application files go last (frequently changed) |
| `USER appuser` | Switches to non-root user for execution | **Security best practice** |
| `CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]` | Default command when container starts | Starts FastAPI server on port 8000 |

### Why Layer Caching Matters

Docker builds images in layers. Each `RUN`, `COPY`, etc. creates a new layer. Docker caches layers and reuses them if nothing changed. The Dockerfile is optimized to:

1. Copy `requirements.txt` first (stable)
2. Install dependencies (takes time)
3. Copy application code last (frequently changes)

This way, if you change your code, Docker doesn't need to reinstall dependencies.

### Building the Docker Image

```bash
# Navigate to project directory
cd /home/timothee/k8s

# Build the image
docker build -t fastapi-k8s .
```

**Breakdown:**

- `docker build`: Build command
- `-t fastapi-k8s`: Tag the image as "fastapi-k8s" (name:version format)
- `.`: Use Dockerfile in current directory

### Testing Locally

```bash
# Run container locally
docker run -p 8000:8000 fastapi-k8s

# Visit http://localhost:8000 in your browser
# Or check Swagger UI: http://localhost:8000/docs
```

---

## Part 2: Kubernetes Basics

### Key Kubernetes Concepts

#### 1. **Pod**

The smallest deployable unit in Kubernetes. Usually contains one container (but can have multiple).

```yaml
# Example: A single pod
apiVersion: v1
kind: Pod
metadata:
  name: fastapi-pod
spec:
  containers:
  - name: fastapi
    image: fastapi-k8s
    ports:
    - containerPort: 8000
```

#### 2. **Deployment**

Manages a set of identical pods. Handles:

- Creating and destroying pods
- Scaling up/down replicas
- Rolling updates
- Self-healing

```yaml
# Example: Deployment with 2 replicas
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 2  # Run 2 copies of the pod
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: fastapi-k8s
        ports:
        - containerPort: 8000
```

#### 3. **Service**

Exposes pods to external traffic. Acts as a stable endpoint for pods (which are ephemeral).

Types of Services:

- **ClusterIP** (default): Only accessible within the cluster
- **NodePort**: Accessible from outside on a specific port
- **LoadBalancer**: Uses cloud provider's load balancer

```yaml
# Example: Service that exposes deployment
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  type: NodePort
  selector:
    app: fastapi  # Matches deployment labels
  ports:
  - port: 80           # External port
    targetPort: 8000   # Container port
```

### How They Work Together

```
┌─────────────────────────────────────────────┐
│           Kubernetes Cluster                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │ Service (fastapi-service)            │  │
│  │ - Listens on port 80                 │  │
│  │ - Routes to pods with label app:fastapi
│  │                                       │  │
│  │  ┌────────────────┐ ┌────────────────┐│
│  │  │ Pod 1          │ │ Pod 2          ││
│  │  │ (fastapi-k8s)  │ │ (fastapi-k8s)  ││
│  │  │ port 8000      │ │ port 8000      ││
│  │  └────────────────┘ └────────────────┘│
│  │                                       │
│  │ Managed by: Deployment                │
│  └──────────────────────────────────────┘│
│                                             │
└─────────────────────────────────────────────┘
         ↑
         │ External Traffic (http://localhost:8000)
         │
    Your Computer
```

---

## Part 3: Deployment Guide

### Step-by-Step Deployment

#### Step 1: Start Minikube

```bash
minikube start
```

This creates a local Kubernetes cluster. It may take a minute or two on first run.

**What happens:**

- Minikube starts a virtual machine (or Docker container)
- Installs Kubernetes components (API server, scheduler, etc.)
- Sets up kubectl to communicate with it

**Verify it's running:**

```bash
kubectl cluster-info
kubectl get nodes
```

#### Step 2: Configure Docker for Minikube

```bash
eval $(minikube docker-env)
```

**Why this matters:** By default, Docker on your host machine is separate from Docker inside Minikube. This command connects your Docker CLI to Minikube's Docker daemon, so the image you build is available to Kubernetes.

**Verify:**

```bash
docker ps  # Should show Minikube's containers
```

#### Step 3: Build the Docker Image

```bash
docker build -t fastapi-k8s .
```

The image is now stored in Minikube's Docker registry and accessible to Kubernetes.

**Verify:**

```bash
docker images | grep fastapi-k8s
```

#### Step 4: Deploy to Kubernetes

```bash
# Create the Deployment
kubectl apply -f deployment.yaml

# Create the Service
kubectl apply -f service.yaml
```

**What happens:**

1. Kubernetes reads `deployment.yaml`
2. Creates 2 pods running the FastAPI container
3. Monitors and restarts them if they fail
4. Kubernetes reads `service.yaml`
5. Creates a service that routes traffic to the pods

**Verify deployment:**

```bash
kubectl get deployments
kubectl get pods
kubectl get services
```

Expected output:

```
NAME                   READY   UP-TO-DATE   AVAILABLE
fastapi-deployment     2/2     2            2

NAME                                  READY   STATUS    RESTARTS
fastapi-deployment-ccf87f4cd-7fg6h    1/1     Running   0
fastapi-deployment-ccf87f4cd-jr8h8    1/1     Running   0

NAME               TYPE      CLUSTER-IP      EXTERNAL-IP   PORT(S)
fastapi-service    NodePort  10.96.123.456   <none>        80:30123/TCP
```

#### Step 5: Access Your Application

```bash
minikube service fastapi-service
```

This command:

1. Finds the external port (e.g., 30123)
2. Gets the Minikube IP (usually 192.168.49.2)
3. Opens your browser to `http://192.168.49.2:30123`

**Alternatively, manually access:**

```bash
# Get the URL
minikube service fastapi-service --url

# Or access directly
curl $(minikube service fastapi-service --url)
```

**Access interactive API docs:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Part 4: Advanced Topics

### Health Checks (Readiness Probes)

In `deployment.yaml`, the readiness probe checks if your application is healthy:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

**How it works:**

- Every 5 seconds, Kubernetes makes an HTTP GET request to `/health`
- If it returns 200, the pod is considered ready
- If it returns an error, traffic is not sent to that pod

**Why it matters:** Prevents sending traffic to pods that aren't ready yet.

**Your app must provide this endpoint:**

```python
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Scaling Replicas

Change the number of running pods:

```bash
# Scale to 5 replicas
kubectl scale deployment fastapi-deployment --replicas=5

# Watch them start
kubectl get pods --watch
```

Or edit the deployment file directly:

```yaml
spec:
  replicas: 5  # Change this number
```

Then apply: `kubectl apply -f deployment.yaml`

### Rolling Updates

Update your code without downtime:

```bash
# 1. Make changes to app.py
# 2. Rebuild the image
eval $(minikube docker-env)
docker build -t fastapi-k8s .

# 3. Restart the deployment (pulls new image)
kubectl rollout restart deployment/fastapi-deployment

# 4. Watch the rollout
kubectl rollout status deployment/fastapi-deployment
```

### Viewing Logs

```bash
# Logs from a specific pod
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>

# Logs from all pods of a deployment
kubectl logs -l app=fastapi --all-containers=true -f
```

### Resource Limits

Specify how much CPU and memory each pod can use:

```yaml
containers:
- name: fastapi
  image: fastapi-k8s
  resources:
    requests:
      memory: "64Mi"
      cpu: "100m"
    limits:
      memory: "128Mi"
      cpu: "500m"
```

**Meanings:**

- `requests`: Kubernetes guarantees at least this much
- `limits`: Container can't exceed this amount
- `m` = millicores (1000m = 1 CPU)
- `Mi` = Mebibytes (1024 bytes)

---

## Troubleshooting

### Issue: "No running pod for service found"

**Cause:** Pods haven't started or are in error state.

**Solution:**

```bash
# Check pod status
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
```

### Issue: "ImagePullBackOff" Error

**Cause:** Kubernetes can't find the Docker image.

**Solution:**

```bash
# Make sure you've set up Minikube's Docker
eval $(minikube docker-env)

# Rebuild the image
docker build -t fastapi-k8s .

# Verify image exists
docker images | grep fastapi-k8s

# Restart deployment
kubectl rollout restart deployment/fastapi-deployment
```

### Issue: Application works locally but not in Kubernetes

**Cause:** Port or configuration mismatch.

**Solution:**

```bash
# Check your app listens on 0.0.0.0:8000 (not just localhost)
# In FastAPI:
uvicorn app:app --host 0.0.0.0 --port 8000

# Check port in Dockerfile matches deployment.yaml
```

### Issue: Connection refused when accessing service

**Cause:** Wrong port or service type issue.

**Solution:**

```bash
# Verify service ports
kubectl get svc

# Port format: <external>:<internal>
# In service.yaml: port: 80 should route to targetPort: 8000

# Test connectivity inside cluster
kubectl run -it --rm debug --image=alpine --restart=Never -- \
  wget -O- http://fastapi-service
```

### General Debugging Commands

```bash
# Show all resources
kubectl get all

# Detailed resource info
kubectl describe deployment fastapi-deployment
kubectl describe service fastapi-service

# View recent events
kubectl get events --sort-by='.lastTimestamp'

# Enter a pod's shell (if it has sh/bash)
kubectl exec -it <pod-name> -- sh

# Copy file from pod
kubectl cp <pod-name>:/app/file.txt ./file.txt

# Check resource usage
kubectl top pods
kubectl top nodes
```

---

## Best Practices Implemented

✅ **Non-root user**: Container runs as `appuser`, not root (security)  
✅ **Lightweight base image**: `python:3.11-slim` (smaller than standard Python image)  
✅ **Layer caching**: Dependencies installed before application code  
✅ **Health checks**: Readiness probe ensures pods are healthy  
✅ **Multiple replicas**: 2 pods provide redundancy and load balancing  
✅ **Service abstraction**: Service provides stable endpoint for ephemeral pods  
✅ **Pip upgrades**: Fresh pip avoids deprecation warnings  
✅ **No cache**: `--no-cache-dir` reduces image size  

---

## Common Development Workflow

```bash
# 1. Start everything
minikube start
eval $(minikube docker-env)

# 2. Make changes to app.py

# 3. Rebuild and redeploy
docker build -t fastapi-k8s .
kubectl rollout restart deployment/fastapi-deployment

# 4. Monitor logs
kubectl logs -f -l app=fastapi

# 5. Access application
minikube service fastapi-service
```

---

## Learning Resources

- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/)

---

## Cleanup

```bash
# Delete all resources
kubectl delete deployment fastapi-deployment
kubectl delete service fastapi-service

# Stop Minikube
minikube stop

# Delete Minikube cluster (be careful!)
minikube delete
```

---

## License

MIT

---

**Last Updated:** February 20, 2026  
**Tutorial Level:** Beginner to Intermediate
