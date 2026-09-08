# JC-KubeScale AI

Kubernetes-native AI Inference & Autoscaling Platform

[![CI](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml/badge.svg)](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28-blue)](https://kubernetes.io)
[![Helm](https://img.shields.io/badge/Helm-3.0-blue)](https://helm.sh)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Problem

LLMs (Large Language Models) have unique operational characteristics:

* High memory and GPU/VRAM usage
* Variable latency depending on model size
* Significant cold starts during model loading
* KV cache that grows with context length
* Limited concurrency per pod
* High infrastructure costs

Running LLMs on Kubernetes requires specialized knowledge of:

* KServe for model serving
* vLLM for optimized inference
* Autoscaling based on inference metrics
* GPU scheduling and quotas
* Observability tailored to AI workloads

## Solution

JC-KubeScale AI is a Kubernetes-native platform that abstracts away the complexity of running LLMs.

**For the API consumer:**

```bash
curl http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Kubernetes in three paragraphs"}'
```

**Response:**

```json
{
  "model": "qwen",
  "response": "Kubernetes is a platform...",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 50
  }
}
```

## Architecture

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
```

## Features

* RESTful API with FastAPI
* Model serving with KServe + vLLM
* Intelligent autoscaling based on inference metrics
* Comprehensive observability (Prometheus, Grafana, Loki, OpenTelemetry)
* GitOps with Argo CD
* CI/CD with GitHub Actions
* Infrastructure as Code with Terraform
* Canary Deployments
* Chaos Engineering
* Defined and monitored SLOs/SLIs

## Quick Start

```bash
# Clone the repository
git clone https://github.com/jacivaldocarvalho/jc-kubescale-ai.git

cd jc-kubescale-ai

# Create a Kind cluster
make cluster

# Install dependencies
make install

# Deploy the platform
make deploy

# Run tests
make test

# Access the API
curl http://localhost:8080/health
```

## Requirements

* Docker 20.10+
* Kubernetes 1.28+ (Kind for development)
* Helm 3.0+
* Go 1.21+ (for some components)
* Python 3.11+ (for the API)
* Make

## API Examples

### Health Check

```bash
curl http://localhost:8080/health
```

### List Models

```bash
curl http://localhost:8080/v1/models
```

### Chat

```bash
curl -X POST http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?"}'
```

### Completions

```bash
curl -X POST http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain machine learning in", "max_tokens": 100}'
```

## Autoscaling

The JC-KubeScale Autoscaler implements logic specific to LLMs:

**Scale Up — Conditions:**

* `queue_depth > threshold`
* `KV cache > 80%`
* `P95 latency > SLO`

**Scale Down — Conditions:**

* `queue_depth ≈ 0`
* KV cache low
* Normal latency

## Observability

Grafana dashboards with the following metrics:

* Requests/s
* P95 Latency
* GPU Utilization
* KV Cache Utilization
* Token throughput
* Active requests
* Model load time

## Security

* Kubernetes RBAC
* Network Policies
* Pod Security Policies
* Kyverno for policies
* TLS for endpoints
* Managed secrets
* Rate Limiting
* JWT/OAuth2 ready

## Roadmap

* **Phase 1**: MVP with a basic API and Kubernetes deployment
* **Phase 2**: Observability (Prometheus, Grafana, Loki, OTel)
* **Phase 3**: Intelligent autoscaling
* **Phase 4**: Model Registry and Canary Deployments
* **Phase 5**: Terraform and production
* **Phase 6**: SRE (Load Testing, Chaos Engineering, SLO)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.
