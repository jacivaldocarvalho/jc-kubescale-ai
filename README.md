# JC-KubeScale AI

Kubernetes-native AI Inference & Autoscaling Platform

[![CI](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml/badge.svg)](https://github.com/jacivaldocarvalho/jc-kubescale-ai/actions/workflows/ci.yaml)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28-blue)](https://kubernetes.io)
[![Helm](https://img.shields.io/badge/Helm-3.0-blue)](https://helm.sh)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Problema

LLMs (Large Language Models) possuem características operacionais únicas:

* Alto consumo de memória e GPU/VRAM
* Latência variável dependendo do tamanho do modelo
* Cold start significativo durante carregamento
* KV cache que cresce com o contexto
* Concorrência limitada por pod
* Custo elevado de infraestrutura

Operar LLMs em Kubernetes exige conhecimento especializado em:

* KServe para serving
* vLLM para inferência otimizada
* Autoscaling baseado em métricas de inferência
* GPU scheduling e quotas
* Observabilidade específica para workloads de IA

## Solução

JC-KubeScale AI é uma plataforma Kubernetes-native que abstrai toda a complexidade de operação de LLMs.

**Para o consumidor:**

```bash
curl http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explique Kubernetes em três parágrafos"}'
```

**Retorno:**

```json
{
  "model": "qwen",
  "response": "Kubernetes é uma plataforma...",
  "usage": {
    "input_tokens": 10,
    "output_tokens": 50
  }
}
```

## Arquitetura

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

* API RESTful com FastAPI
* Model Serving com KServe + vLLM
* Autoscaling inteligente baseado em métricas de inferência
* Observabilidade completa (Prometheus, Grafana, Loki, OpenTelemetry)
* GitOps com Argo CD
* CI/CD com GitHub Actions
* Infrastructure as Code com Terraform
* Canary Deployments
* Chaos Engineering
* SLO/SLI definidos e monitorados

## Quick Start

```bash
# Clone o repositório
git clone https://github.com/jacivaldocarvalho/jc-kubescale-ai.git

cd jc-kubescale-ai

# Cria cluster Kind
make cluster

# Instala dependências
make install

# Deploy da plataforma
make deploy

# Executa testes
make test

# Acessa a API
curl http://localhost:8080/health
```

## Requisitos

* Docker 20.10+
* Kubernetes 1.28+ (Kind para desenvolvimento)
* Helm 3.0+
* Go 1.21+ (para alguns componentes)
* Python 3.11+ (para API)
* Make

## Exemplos de API

### Health Check

```bash
curl http://localhost:8080/health
```

### Listar Modelos

```bash
curl http://localhost:8080/v1/models
```

### Chat

```bash
curl -X POST http://localhost:8080/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "O que é inteligência artificial?"}'
```

### Completions

```bash
curl -X POST http://localhost:8080/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explique machine learning em", "max_tokens": 100}'
```

## Autoscaling

O JC-KubeScale Autoscaler implementa lógica específica para LLMs:

**Scale Up — Condições:**

* `queue_depth > threshold`
* `KV cache > 80%`
* `P95 latency > SLO`

**Scale Down — Condições:**

* `queue_depth ≈ 0`
* KV cache low
* Latência normal

## Observabilidade

Dashboards Grafana com métricas:

* Requests/s
* P95 Latency
* GPU Utilization
* KV Cache Utilization
* Token throughput
* Active requests
* Model load time

## Segurança

* RBAC no Kubernetes
* Network Policies
* Pod Security Policies
* Kyverno para policies
* TLS para endpoints
* Secrets gerenciados
* Rate Limiting
* JWT/OAuth2 preparado

## Roadmap

* **Fase 1**: MVP com API básica e deploy Kubernetes
* **Fase 2**: Observabilidade (Prometheus, Grafana, Loki, OTel)
* **Fase 3**: Autoscaling inteligente
* **Fase 4**: Model Registry e Canary Deployments
* **Fase 5**: Terraform e produção
* **Fase 6**: SRE (Load Testing, Chaos Engineering, SLO)

## Contribuição

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## Licença

Este projeto está licenciado sob a **MIT License**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.
