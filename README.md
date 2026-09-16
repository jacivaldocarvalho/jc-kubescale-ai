# JC-KubeScale AI

Kubernetes-Native AI Inference & Autoscaling Platform

[![CI](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml/badge.svg)](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28-blue)](https://kubernetes.io)
[![Helm](https://img.shields.io/badge/Helm-3.0-blue)](https://helm.sh)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Prometheus](https://img.shields.io/badge/Prometheus-2.51-orange)](https://prometheus.io)
[![Grafana](https://img.shields.io/badge/Grafana-10.4-orange)](https://grafana.com)
[![KEDA](https://img.shields.io/badge/KEDA-2.14-blue)](https://keda.sh)
[![Phase](https://img.shields.io/badge/Phase-3-yellow)](https://github.com/jacivaldocarvalho/jc-kubescale-ai)

## Project Status

**PHASE 3 - Intelligent Autoscaling Completed**

| Phase | Description | Status |
|-------|-------------|--------|
| **PHASE 1** | MVP with basic API and Kubernetes deployment | Completed |
| **PHASE 2** | Observability (Prometheus, Grafana, Loki, OTel) | Completed |
| **PHASE 3** | Intelligent autoscaling | Completed |
| **PHASE 4** | Model Registry and Canary Deployments | Next |

## Problem

LLMs (Large Language Models) have unique operational characteristics:

- High memory and GPU/VRAM consumption
- Variable latency depending on model size
- Significant cold-start time during model loading
- KV cache growth as context size increases
- Limited concurrency per pod
- High infrastructure costs

Operating LLMs on Kubernetes requires specialized knowledge of:

- KServe for model serving
- vLLM for optimized inference
- Autoscaling based on inference metrics
- GPU scheduling and quotas
- Observability tailored to AI workloads

## Solution

JC-KubeScale AI is a Kubernetes-native platform that abstracts the operational complexity of running LLMs.

**For API consumers:**

```bash
curl http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Kubernetes in three paragraphs"}'
```

**Response:**

```json
{
  "model": "qwen",
  "response": "Kubernetes is an open-source platform for container orchestration. It automates the deployment, scaling, and management of containerized applications. Kubernetes groups containers into pods to simplify management.",
  "usage": {
    "input_tokens": 5,
    "output_tokens": 24,
    "total_tokens": 29
  }
}
```

## Current Architecture (PHASE 3)

```
                         CLIENT
                            │
                            ▼
                    ┌─────────────────┐
                    │  localhost:8080 │
                    │    (NodePort)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Service     │
                    │ jc-kubescale-api│
                    │    NodePort     │
                    │   30080:8080    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Deployment    │
                    │ jc-kubescale-api│
                    │  Replicas: 1→10 │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      Pod        │
                    │  Container: api │
                    │   FastAPI App   │
                    │                 │
                    │  /health        │
                    │  /ready         │
                    │  /metrics       │
                    │  /v1/models     │
                    │  /v1/chat       │
                    │  /v1/completions│
                    └─────────────────┘
                             ▲
                             │
                    ┌────────┴────────┐
                    │   Autoscaling   │
                    │                 │
                    │  ┌───────────┐  │
                    │  │   KEDA    │  │
                    │  │ ScaledObject│ │
                    │  │   HPA     │  │
                    │  └─────┬─────┘  │
                    │        │        │
                    │  ┌─────┴─────┐  │
                    │  │Autoscaler │  │
                    │  │ JC-KubeScale│ │
                    │  └───────────┘  │
                    └─────────────────┘


        ┌───────────────────────────────────────┐
        │           OBSERVABILITY                │
        │                                       │
        │  ┌─────────────┐  ┌─────────────┐    │
        │  │ Prometheus  │  │   Grafana   │    │
        │  │  (Metrics)  │  │  (Dashboards)│    │
        │  └──────┬──────┘  └──────┬──────┘    │
        │         │                │            │
        │  ┌──────┴──────┐  ┌──────┴──────┐    │
        │  │    Loki     │  │    OTel     │    │
        │  │   (Logs)    │  │  (Traces)   │    │
        │  └─────────────┘  └─────────────┘    │
        │                                       │
        │  Grafana: http://localhost:3000      │
        │  Prometheus: http://localhost:9090   │
        │  Loki: http://localhost:3100         │
        └───────────────────────────────────────┘
```

## Planned Architecture (Complete)

```
                         INTERNET
                            │
                            ▼
                    ┌─────────────────┐
                    │   API Gateway   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  JC-KubeScale   │
                    │    AI Gateway   │
                    │                 │
                    │ Auth            │
                    │ Rate Limit      │
                    │ Model Routing   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     KServe      │
                    │                 │
                    │ Model Serving   │
                    │ Autoscaling     │
                    │ Deployment      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      vLLM       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │       LLM       │
                    │      Qwen       │
                    └─────────────────┘


        ┌───────────────────────────────────────┐
        │           OBSERVABILITY                │
        │                                       │
        │ Prometheus │ Grafana │ Loki │ OTel    │
        └───────────────────────────────────────┘


        ┌───────────────────────────────────────┐
        │              PLATFORM                 │
        │                                       │
        │ Kubernetes │ KEDA │ Argo CD │ Kyverno │
        └───────────────────────────────────────┘
```

## Implemented Features (PHASE 1)

- [x] RESTful API with FastAPI
- [x] Kubernetes deployment using Kind with NodePort
- [x] Direct access through port 8080 without port forwarding
- [x] Health, readiness, and metrics endpoints
- [x] Chat and completions endpoints
- [x] Mock inference for development
- [x] Structured JSON logging
- [x] Basic Prometheus metrics
- [x] Makefile for task automation
- [x] Setup and verification scripts
- [x] Technical and beginner-friendly documentation

## Implemented Features (PHASE 2)

- [x] Prometheus for metrics collection
- [x] Grafana for visualization
- [x] Loki for log aggregation
- [x] OpenTelemetry Collector for traces
- [x] Grafana dashboards provisioned via ConfigMap
- [x] Persistent storage for Grafana (PVC)
- [x] RBAC for Prometheus pod discovery
- [x] Annotations for Prometheus auto-discovery
- [x] Automated port-forwarding
- [x] Health checks and readiness probes

## Implemented Features (PHASE 3)

- [x] KEDA for event-driven autoscaling
- [x] JC-KubeScale Autoscaler service
- [x] LLM-specific metrics (queue_depth, kv_cache, p95_latency)
- [x] ScaledObject with Prometheus triggers
- [x] RBAC for autoscaler
- [x] HPA with scaling policies
- [x] Scale up based on queue_depth, KV cache, P95 latency
- [x] Scale down based on low utilization
- [x] Manual scaling endpoint
- [x] Reconciliation loop

## Planned Features

- [ ] Model serving with KServe + vLLM
- [ ] GitOps with Argo CD
- [ ] Complete CI/CD pipeline with GitHub Actions
- [ ] Infrastructure as Code with Terraform
- [ ] Canary deployments
- [ ] Chaos engineering
- [ ] Defined and monitored SLOs/SLIs

## Quick Start

### Prerequisites

- Docker 20.10+
- Kubernetes 1.28+ (Kind for development)
- Helm 3.0+
- Python 3.11+
- Make

### Automated Installation

```bash
# 1. Clone the repository
git clone https://github.com/jacivaldocarvalho/jc-kubescale-ai.git
cd jc-kubescale-ai

# 2. Install tools (Linux)
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Full Deployment

```bash
# Run the complete setup
make all

# Deploy observability stack
make deploy-observability

# Deploy autoscaling stack
make deploy-autoscaling

# Test the API without port forwarding
curl http://localhost:8080/health
```

### Make Commands

| Command | Description |
|---------|-------------|
| `make all` | Runs the complete setup |
| `make cluster` | Creates the Kind cluster |
| `make install` | Installs dependencies |
| `make build` | Builds the Docker image |
| `make load-image` | Loads the image into Kind |
| `make deploy` | Deploys the API |
| `make deploy-observability` | Deploys observability stack |
| `make deploy-autoscaling` | Deploys autoscaling stack |
| `make status` | Shows deployment status |
| `make status-observability` | Shows observability status |
| `make status-autoscaling` | Shows autoscaling status |
| `make logs` | Displays API logs |
| `make logs-observability` | Displays observability logs |
| `make logs-autoscaler` | Displays autoscaler logs |
| `make test-api` | Tests API endpoints |
| `make port-forward-all` | Starts all port-forwards |
| `make port-forward-stop` | Stops all port-forwards |
| `make undeploy` | Removes the API deployment |
| `make undeploy-observability` | Removes observability (preserves PVC) |
| `make undeploy-observability-clean` | Removes observability completely |
| `make undeploy-autoscaling` | Removes autoscaling |
| `make clean` | Performs a full cleanup |

## API Examples

### Health Check

```bash
curl http://localhost:8080/health
```

Response:

```json
{"status": "healthy", "timestamp": 1736376173.123456}
```

### Readiness

```bash
curl http://localhost:8080/ready
```

Response:

```json
{"status": "ready", "inference": true}
```

### List Models

```bash
curl http://localhost:8080/v1/models
```

Response:

```json
{
  "models": [
    {
      "name": "qwen",
      "version": "1",
      "status": "ready",
      "metadata": null
    }
  ]
}
```

### Chat

```bash
curl -X POST http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?"}'
```

Response:

```json
{
  "model": "qwen",
  "response": "Artificial Intelligence is a field of computer science focused on creating systems capable of performing tasks that normally require human intelligence.",
  "usage": {
    "input_tokens": 5,
    "output_tokens": 18,
    "total_tokens": 23
  },
  "metadata": null
}
```

### Completions

```bash
curl -X POST http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Machine learning is a field of", "max_tokens": 50}'
```

Response:

```json
{
  "model": "qwen",
  "text": "Completing: Machine learning is a field of... This is a mock response for demonstration purposes.",
  "usage": {
    "input_tokens": 8,
    "output_tokens": 12,
    "total_tokens": 20
  }
}
```

### Metrics (Prometheus)

```bash
curl http://localhost:8080/metrics
```

## Observability

### Accessing the Stack

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |

### Metrics Collected

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_latency_seconds` | Histogram | Request latency |
| `http_active_requests` | Gauge | Active requests |
| `tokens_input_total` | Counter | Input tokens |
| `tokens_output_total` | Counter | Output tokens |
| `queue_depth` | Gauge | Current queue depth |
| `kv_cache_utilization` | Gauge | KV cache utilization percentage |
| `tokens_per_second` | Gauge | Tokens per second |

### Grafana Dashboards

The following dashboard is provisioned automatically:

- **JC-KubeScale AI - Overview:** Requests/s, P95 Latency, Active Requests, Error Rate, Tokens/s, Pod Status

### Logs with Loki

Logs are collected by Loki and can be queried in Grafana:

1. Access Grafana at http://localhost:3000
2. Navigate to **Explore**
3. Select **Loki** as datasource
4. Query: `{namespace="jc-kubescale"}`

### Traces with OpenTelemetry

The OTel Collector receives traces from the API and exports them for analysis.

## Autoscaling

### Architecture

The JC-KubeScale Autoscaler scales the API based on inference-specific metrics:

```
┌─────────────────────────────────────────────────────────────┐
│                    Autoscaling Stack                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              JC-KubeScale Autoscaler                │   │
│  │  - queue_depth                                      │   │
│  │  - KV cache utilization                             │   │
│  │  - P95 latency                                      │   │
│  │  - tokens_per_second                                │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    KEDA                             │   │
│  │  - ScaledObject                                     │   │
│  │  - HPA                                              │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Deployment (API)                       │   │
│  │  Replicas: 1 → 10                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Scaling Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| `queue_depth` | 5 | Queue depth |
| `kv_cache_utilization` | 80% | KV cache usage |
| `p95_latency` | 2s | P95 latency |

### Scale Up Conditions

- `queue_depth > 5`
- `KV cache > 80%`
- `P95 latency > 2s`

### Scale Down Conditions

- `queue_depth ≈ 0`
- `KV cache < 30%`
- `P95 latency < 0.5s`

### Autoscaler API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/ready` | GET | Readiness probe |
| `/metrics` | GET | Prometheus metrics |
| `/v1/metrics` | GET | Current metrics |
| `/v1/replicas` | GET | Current replica count |
| `/v1/reconcile` | POST | Trigger reconciliation |
| `/v1/scale?replicas=N` | POST | Manual scaling |

### Commands

```bash
# Deploy autoscaling
make deploy-autoscaling

# Check status
make status-autoscaling

# View logs
make logs-autoscaler

# Remove autoscaling
make undeploy-autoscaling
```

### Testing

```bash
# Generate load
for i in {1..100}; do
  curl -s http://localhost:8080/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "teste '$i'"}' > /dev/null &
done
wait

# Check scaling
kubectl get hpa -n jc-kubescale -w
```

## Project Structure

```
jc-kubescale-ai/
├── README.md                 # Main documentation
├── LICENSE                   # MIT License
├── Makefile                  # Task automation
├── CONTRIBUTING.md           # Contribution guide
├── .gitignore                # Files ignored by Git
├── .dockerignore             # Files ignored by Docker
├── setup-project.sh          # Initial setup script
│
├── scripts/
│   └── setup.sh             # Tool installation
│
├── infrastructure/
│   └── kind/
│       └── kind-config.yaml # Kind configuration
│
├── services/
│   ├── api/
│   │   ├── Dockerfile       # API image
│   │   ├── Dockerfile.dev   # Development mode
│   │   ├── requirements.txt # Python dependencies
│   │   ├── pyproject.toml   # Project configuration
│   │   └── src/
│   │       ├── __init__.py
│   │       ├── main.py      # Entry point
│   │       ├── app/
│   │       │   ├── __init__.py
│   │       │   ├── api/     # Endpoints and routes
│   │       │   ├── core/    # Configuration and logging
│   │       │   ├── models/  # Pydantic schemas
│   │       │   └── services/# Business logic
│   │       └── tests/       # Unit tests
│   │
│   └── autoscaler/          # JC-KubeScale Autoscaler
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           ├── __init__.py
│           ├── main.py
│           ├── app/
│           │   ├── __init__.py
│           │   ├── api/
│           │   ├── core/
│           │   └── services/
│           └── tests/
│
├── deploy/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── api-deployment.yaml
│   │   └── api-service.yaml
│   │
│   ├── observability/
│   │   ├── prometheus-configmap.yaml
│   │   ├── prometheus-rules-configmap.yaml
│   │   ├── prometheus-rbac.yaml
│   │   ├── prometheus-deployment.yaml
│   │   ├── grafana-configmap.yaml
│   │   ├── grafana-pvc.yaml
│   │   ├── grafana-deployment.yaml
│   │   ├── loki-configmap.yaml
│   │   ├── loki-deployment.yaml
│   │   ├── otel-configmap.yaml
│   │   └── otel-collector.yaml
│   │
│   └── autoscaling/
│       ├── autoscaler-rbac.yaml
│       ├── autoscaler-deployment.yaml
│       ├── autoscaler-service.yaml
│       ├── scaledobject.yaml
│       ├── triggerauthentication.yaml
│       └── keda-install.yaml
│
├── charts/
│   └── jc-kubescale/        # Helm Chart
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       └── templates/
│
├── docs/
│   ├── phase-1-api.md           # Phase 1 documentation
│   ├── phase-2-observability.md # Phase 2 documentation
│   └── phase-3-autoscaling.md   # Phase 3 documentation
│
├── tests/                    # Tests
│   ├── unit/
│   ├── integration/
│   ├── load/
│   └── chaos/
│
└── .github/
    └── workflows/
        └── ci.yaml          # CI/CD pipeline
```

## Documentation

| Document | Description |
|----------|-------------|
| [Phase 1 - API](docs/phase-1-api.md) | Technical guide for the API |
| [Phase 2 - Observability](docs/phase-2-observability.md) | Technical guide for observability |
| [Phase 3 - Autoscaling](docs/phase-3-autoscaling.md) | Technical guide for autoscaling |

## Security (Planned)

- Kubernetes RBAC
- Network Policies
- Pod Security Policies
- Kyverno for policy enforcement
- TLS for endpoints
- Managed secrets
- Rate limiting
- JWT/OAuth2 support

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| **PHASE 1** | MVP with basic API and Kubernetes deployment | Completed |
| **PHASE 2** | Observability (Prometheus, Grafana, Loki, OTel) | Completed |
| **PHASE 3** | Intelligent autoscaling | Completed |
| **PHASE 4** | Model Registry and Canary Deployments | Next |
| **PHASE 5** | Terraform and production environments (AWS/GCP/Azure) | Planned |
| **PHASE 6** | SRE (Load Testing, Chaos Engineering, SLOs) | Planned |

## Contributing

1. Fork the project.
2. Create a branch for your feature (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## Author

**Jacivaldo Carvalho**
Telecommunications Engineer | DevOps | SRE | Networking

## Acknowledgments

- Kubernetes community
- FastAPI
- Kind
- Helm
- Prometheus
- Grafana
- Loki
- OpenTelemetry
- KEDA

