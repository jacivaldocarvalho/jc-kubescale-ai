# JC-KubeScale AI - PHASE 1: API

## Overview

PHASE 1 establishes the foundation of the JC-KubeScale AI platform by implementing a RESTful API with FastAPI running inside Kubernetes. The API provides endpoints for LLM inference through an abstraction layer.

## Current Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                  │
│                    (curl, browser, app)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP :8080
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KIND CLUSTER                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   NAMESPACE: jc-kubescale                 │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           SERVICE: jc-kubescale-api                │  │  │
│  │  │              Type: ClusterIP                       │  │  │
│  │  │              Port: 8080                            │  │  │
│  │  └─────────────────────┬───────────────────────────────┘  │  │
│  │                        │                                   │  │
│  │                        ▼                                   │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           DEPLOYMENT: jc-kubescale-api             │  │  │
│  │  │              Replicas: 1                           │  │  │
│  │  │  ┌─────────────────────────────────────────────┐    │  │  │
│  │  │  │              POD                            │    │  │  │
│  │  │  │  ┌───────────────────────────────────────┐  │    │  │  │
│  │  │  │  │        CONTAINER: api                 │  │    │  │  │
│  │  │  │  │  Image: jc-kubescale-api:latest      │  │    │  │  │
│  │  │  │  │  Port: 8080                           │  │    │  │  │
│  │  │  │  │                                       │  │    │  │  │
│  │  │  │  │  ┌─────────────────────────────────┐  │  │    │  │  │
│  │  │  │  │  │      FASTAPI APPLICATION        │  │  │    │  │  │
│  │  │  │  │  │  ┌───────────────────────────┐  │  │  │    │  │  │
│  │  │  │  │  │  │  /health                  │  │  │  │    │  │  │
│  │  │  │  │  │  │  /ready                   │  │  │  │    │  │  │
│  │  │  │  │  │  │  /metrics                 │  │  │  │    │  │  │
│  │  │  │  │  │  │  /v1/models               │  │  │  │    │  │  │
│  │  │  │  │  │  │  /v1/chat                 │  │  │  │    │  │  │
│  │  │  │  │  │  │  /v1/completions          │  │  │  │    │  │  │
│  │  │  │  │  │  └───────────────────────────┘  │  │  │    │  │  │
│  │  │  │  │  └─────────────────────────────────┘  │  │    │  │  │
│  │  │  │  └───────────────────────────────────────┘  │    │  │  │
│  │  │  └─────────────────────────────────────────────┘    │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## API Directory Structure

```text
services/api/
├── Dockerfile               # Container image
├── requirements.txt         # Python dependencies
├── src/
│   ├── main.py              # FastAPI entry point
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py       # API endpoints
│   │   │   ├── models.py       # Pydantic schemas
│   │   │   └── dependencies.py # Dependency injection
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py       # Configuration
│   │   │   ├── logging.py      # Structured logging
│   │   │   └── exceptions.py   # Custom exceptions
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py      # Response schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       └── inference.py    # Inference logic (mock)
│   └── tests/
│       ├── __init__.py
│       ├── test_health.py
│       └── test_chat.py
└── Dockerfile.dev           # Development mode
```

## Request Flow

```text
1. Client sends an HTTP request
        │
        ▼
2. Service (ClusterIP) forwards it to the Pod
        │
        ▼
3. FastAPI receives the request
        │
        ▼
4. Middleware collects metrics (Prometheus)
        │
        ▼
5. Router forwards the request to the appropriate endpoint
        │
        ▼
6. InferenceService processes the request (mock)
        │
        ▼
7. Returns a JSON response
```

## Commands for Execution and Testing

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/jacivaldocarvalho/jc-kubescale-ai.git

cd jc-kubescale-ai

# 2. Install tools (Linux)
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Check the environment
chmod +x scripts/check-env.sh
./scripts/check-env.sh
```

### Deploy to Kubernetes

```bash
# 1. Create the Kind cluster
make cluster

# 2. Install dependencies
make install

# 3. Build and deploy
make deploy

# 4. Check status
make status
```

### Tests

```bash
# 1. Unit tests (local)
make test

# 2. API tests (requires port forwarding)
make test-api

# 3. Manual tests
curl http://localhost:8080/health

curl http://localhost:8080/v1/models

curl -X POST http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Test"}'
```

### Logs and Debugging

```bash
# 1. View API logs
make logs

# 2. View detailed logs
kubectl logs -n jc-kubescale -l app=jc-kubescale-api --tail=100

# 3. Describe the pod for troubleshooting
kubectl describe pod -n jc-kubescale -l app=jc-kubescale-api

# 4. Access the container shell
kubectl exec -it -n jc-kubescale deployment/jc-kubescale-api -- /bin/bash
```

### Cleanup

```bash
# 1. Remove the deployment
make undeploy

# 2. Remove the cluster
make cluster-delete

# 3. Full cleanup
make clean
```

## Common Troubleshooting

### Error: `kind: command not found`

```bash
# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64

chmod +x ./kind

sudo mv ./kind /usr/local/bin/kind
```

### Error: Pod in CrashLoopBackOff

```bash
# 1. View logs
kubectl logs -n jc-kubescale -l app=jc-kubescale-api

# 2. Check whether the image exists
docker images | grep jc-kubescale-api

# 3. Rebuild and reload
make build

make load-image

kubectl rollout restart deployment jc-kubescale-api -n jc-kubescale
```

### Error: Port Forwarding Does Not Work

```bash
# 1. Check whether the pod is running
kubectl get pods -n jc-kubescale

# 2. Restart port forwarding
pkill -f "kubectl port-forward.*8080"

kubectl port-forward -n jc-kubescale svc/jc-kubescale-api 8080:8080

# 3. Try an alternative port
kubectl port-forward -n jc-kubescale svc/jc-kubescale-api 8081:8080

curl http://localhost:8081/health
```

### Error: `ModuleNotFoundError: No module named 'app'`

```bash
# Check the __init__.py structure
cd services/api/src

find . -name "*.py" | sort

# It should include:
# ./app/__init__.py
# ./app/api/__init__.py
# ./app/core/__init__.py
# ./app/models/__init__.py
# ./app/services/__init__.py
# ./__init__.py
```

## Available Metrics (Prometheus)

| Metric                         | Type      | Description                   |
| ------------------------------ | --------- | ----------------------------- |
| `http_requests_total`          | Counter   | Total number of HTTP requests |
| `http_request_latency_seconds` | Histogram | Request latency               |
| `http_active_requests`         | Gauge     | Active requests               |

Endpoint: `GET /metrics`

## API Endpoints

| Method | Endpoint          | Description            |
| ------ | ----------------- | ---------------------- |
| GET    | `/health`         | Health check           |
| GET    | `/ready`          | Readiness probe        |
| GET    | `/metrics`        | Prometheus metrics     |
| GET    | `/v1/models`      | Lists available models |
| POST   | `/v1/chat`        | Chat with an LLM       |
| POST   | `/v1/completions` | Completions            |

### Example: `POST /v1/chat`

**Request:**

```json
{
  "message": "What is Kubernetes?",
  "model": "qwen",
  "temperature": 0.7,
  "max_tokens": 512
}
```

**Response:**

```json
{
  "model": "qwen",
  "response": "Kubernetes is a platform...",
  "usage": {
    "input_tokens": 5,
    "output_tokens": 24,
    "total_tokens": 29
  }
}
```

## Validation Checklist

* [ ] `make cluster` creates the Kind cluster
* [ ] `make install` installs dependencies
* [ ] `make build` builds the Docker image
* [ ] `make load-image` loads the image into Kind
* [ ] `make deploy` deploys the API
* [ ] `make status` displays the resources
* [ ] `make test-api` tests the endpoints
* [ ] `curl http://localhost:8080/health` returns HTTP 200
* [ ] `curl http://localhost:8080/v1/models` lists the available models
* [ ] `curl -X POST http://localhost:8080/v1/chat` returns a response
* [ ] `make undeploy` removes the resources
* [ ] `make cluster-delete` removes the cluster

## Next Steps (PHASE 2)

1. Install Prometheus for metrics collection
2. Install Grafana for dashboards
3. Configure Loki for centralized logging
4. Implement OpenTelemetry for tracing
5. Create observability dashboards
