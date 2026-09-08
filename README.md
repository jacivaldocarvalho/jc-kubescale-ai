# JC-KubeScale AI

Kubernetes-Native AI Inference & Autoscaling Platform

[![CI](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml/badge.svg)](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml) [![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28-blue)](https://kubernetes.io) [![Helm](https://img.shields.io/badge/Helm-3.0-blue)](https://helm.sh) [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com) [![Phase](https://img.shields.io/badge/Phase-1-yellow)](https://github.com/jacivaldocarvalho/jc-kubescale-ai)

## Project Status

**PHASE 1 - MVP Completed**

* [x] RESTful API with FastAPI
* [x] Kubernetes deployment using Kind
* [x] Endpoints: `/health`, `/ready`, `/v1/models`, `/v1/chat`, `/v1/completions`
* [x] Basic Prometheus metrics
* [x] Structured JSON logging
* [x] Makefile for automation
* [x] Initial documentation

**Next Phase:** Observability (Prometheus, Grafana, Loki, OpenTelemetry)

## Problem

LLMs (Large Language Models) have unique operational characteristics:

* High memory and GPU/VRAM consumption
* Variable latency depending on model size
* Significant cold-start time during model loading
* KV cache growth as context size increases
* Limited concurrency per pod
* High infrastructure costs

Operating LLMs on Kubernetes requires specialized knowledge of:

* KServe for model serving
* vLLM for optimized inference
* Autoscaling based on inference metrics
* GPU scheduling and quotas
* Observability tailored to AI workloads

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

## Current Architecture (PHASE 1)

```text
                         CLIENT
                           │
                           ▼
                    ┌─────────────────┐
                    │  localhost:8080 │
                    │   (NodePort)    │
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
                    │    Replicas: 1  │
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
```

## Planned Architecture (Complete)

```text
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
        │            OBSERVABILITY              │
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

* [x] RESTful API with FastAPI
* [x] Kubernetes deployment using Kind with NodePort
* [x] Direct access through port 8080 without port forwarding
* [x] Health, readiness, and metrics endpoints
* [x] Chat and completions endpoints
* [x] Mock inference for development
* [x] Structured JSON logging
* [x] Basic Prometheus metrics
* [x] Makefile for task automation
* [x] Setup and verification scripts
* [x] Technical and beginner-friendly documentation

## Planned Features

* [ ] Model serving with KServe + vLLM
* [ ] Intelligent autoscaling based on inference metrics
* [ ] Full observability stack (Prometheus, Grafana, Loki, OpenTelemetry)
* [ ] GitOps with Argo CD
* [ ] Complete CI/CD pipeline with GitHub Actions
* [ ] Infrastructure as Code with Terraform
* [ ] Canary deployments
* [ ] Chaos engineering
* [ ] Defined and monitored SLOs/SLIs

## Quick Start

### Prerequisites

* Docker 20.10+
* Kubernetes 1.28+ (Kind for development)
* Helm 3.0+
* Python 3.11+
* Make

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

# Test the API without port forwarding
curl http://localhost:8080/health
```

### Make Commands

| Command           | Description               |
| ----------------- | ------------------------- |
| `make all`        | Runs the complete setup   |
| `make cluster`    | Creates the Kind cluster  |
| `make install`    | Installs dependencies     |
| `make build`      | Builds the Docker image   |
| `make load-image` | Loads the image into Kind |
| `make deploy`     | Deploys the platform      |
| `make status`     | Shows deployment status   |
| `make logs`       | Displays logs             |
| `make test-api`   | Tests API endpoints       |
| `make undeploy`   | Removes the deployment    |
| `make clean`      | Performs a full cleanup   |

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

## Project Structure

```text
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
│   └── api/
│       ├── Dockerfile       # API image
│       ├── Dockerfile.dev   # Development mode
│       ├── requirements.txt # Python dependencies
│       ├── pyproject.toml   # Project configuration
│       └── src/
│           ├── __init__.py
│           ├── main.py      # Entry point
│           ├── app/
│           │   ├── __init__.py
│           │   ├── api/     # Endpoints and routes
│           │   ├── core/    # Configuration and logging
│           │   ├── models/  # Pydantic schemas
│           │   └── services/# Business logic
│           └── tests/       # Unit tests
│
├── deploy/
│   └── base/
│       ├── namespace.yaml
│       ├── api-deployment.yaml
│       └── api-service.yaml
│
├── charts/
│   └── jc-kubescale/        # Helm Chart
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       └── templates/

│
├── tests/                    # Tests
│   ├── unit/
│   ├── integration/
│   ├── load/
│   └── chaos/
│
└── .github/
    └── workflows/
        └── ci.yaml          # Basic CI/CD
```

## Autoscaling (Planned)

The JC-KubeScale Autoscaler will implement LLM-specific scaling logic:

**Scale Up — Conditions:**

* `queue_depth > threshold`
* `KV cache > 80%`
* `P95 latency > SLO`

**Scale Down — Conditions:**

* `queue_depth ≈ 0`
* `KV cache low`
* `Normal latency`

## Observability (Planned)

Grafana dashboards will include the following metrics:

* Requests/s
* P95 latency
* GPU utilization
* KV cache utilization
* Token throughput
* Active requests
* Model load time
* Pod restarts

## Security (Planned)

* Kubernetes RBAC
* Network Policies
* Pod Security Policies
* Kyverno for policy enforcement
* TLS for endpoints
* Managed secrets
* Rate limiting
* JWT/OAuth2 support

## Roadmap

| Phase       | Description                                           | Status    |
| ----------- | ----------------------------------------------------- | --------- |
| **PHASE 1** | MVP with basic API and Kubernetes deployment          | Completed |
| **PHASE 2** | Observability (Prometheus, Grafana, Loki, OTel)       | Next      |
| **PHASE 3** | Intelligent autoscaling                               | Planned   |
| **PHASE 4** | Model Registry and Canary Deployments                 | Planned   |
| **PHASE 5** | Terraform and production environments (AWS/GCP/Azure) | Planned   |
| **PHASE 6** | SRE (Load Testing, Chaos Engineering, SLOs)           | Planned   |

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

**Jacivaldo Carvalho** - [GitHub](https://github.com/jacivaldocarvalho)

## Acknowledgments

* Kubernetes community
* FastAPI
* Kind
* Helm
* Prometheus
* Grafana
