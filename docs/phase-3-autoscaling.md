# FASE 3 - Intelligent Autoscaling

## Overview

Phase 3 implements the JC-KubeScale Autoscaler, a custom component that scales LLM workloads based on inference-specific metrics, not just CPU/memory.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JC-KubeScale AI                          │
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

## Components

| Component | Function |
|-----------|----------|
| **KEDA** | Event-driven autoscaling |
| **JC-KubeScale Autoscaler** | LLM-specific scaling logic |
| **ScaledObject** | Defines scaling triggers |
| **HPA** | Manages replica count |

## Scaling Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| `queue_depth` | 5 | Queue depth |
| `kv_cache_utilization` | 80% | KV cache usage |
| `p95_latency` | 2s | P95 latency |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /ready` | Readiness probe |
| `GET /metrics` | Prometheus metrics |
| `GET /v1/metrics` | Current metrics |
| `GET /v1/replicas` | Current replica count |
| `POST /v1/reconcile` | Trigger reconciliation |
| `POST /v1/scale?replicas=N` | Manual scaling |

## Commands

```bash
# Deploy
make deploy-autoscaling

# Status
make status-autoscaling

# Logs
make logs-autoscaler

# Undeploy
make undeploy-autoscaling
```

## Testing

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

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ScaledObject `READY=False` | Check KEDA logs |
| HPA `<unknown>` | Check Prometheus metrics |
| Query returns multiple elements | Aggregate with `sum() by (le)` |
| Autoscaler CrashLoopBackOff | Check `logging.py` and `__init__.py` |

## Security

- RBAC with least privilege
- ServiceAccount for autoscaler
- No secrets in manifests
