# JC-KubeScale AI - FASE 2: Observabilidade

## Visão Geral

A FASE 2 do JC-KubeScale AI implementa uma stack completa de observabilidade para monitorar a plataforma de inferência de LLMs. O objetivo é fornecer visibilidade sobre métricas, logs e traces, permitindo identificar problemas, otimizar performance e garantir confiabilidade.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         JC-KUBESCALE AI                                │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      API (FastAPI)                              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐│   │
│  │  │  /metrics  │  /v1/chat  │  /v1/models  │  /v1/completions ││   │
│  │  └─────────────────────────────────────────────────────────────┘│   │
│  └───────────────────────────┬─────────────────────────────────────┘   │
│                              │                                          │
│  ┌───────────────────────────┼─────────────────────────────────────┐   │
│  │                           │                                     │   │
│  │  ┌────────────────────────┴────────────────────────┐           │   │
│  │  │              OpenTelemetry Collector              │           │   │
│  │  │          (recebe traces da API)                  │           │   │
│  │  └────────────────────────┬────────────────────────┘           │   │
│  │                           │                                     │   │
│  │  ┌────────────────────────┼────────────────────────┐           │   │
│  │  │                        │                        │           │   │
│  │  ▼                        ▼                        ▼           │   │
│  │ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │ │  Prometheus  │  │    Loki     │  │  OTel/Tempo  │        │   │
│  │ │  (Metricas)  │  │   (Logs)    │  │   (Traces)   │        │   │
│  │ └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │   │
│  │        │                 │                 │                  │   │
│  │        └─────────────────┼─────────────────┘                  │   │
│  │                          │                                    │   │
│  │                          ▼                                    │   │
│  │              ┌─────────────────────┐                         │   │
│  │              │      Grafana        │                         │   │
│  │              │    (Visualizacao)   │                         │   │
│  │              └─────────────────────┘                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Componentes

| Componente | Função | Porta | URL de Acesso |
|------------|--------|-------|---------------|
| **Prometheus** | Coleta e armazena métricas | 9090 | http://localhost:9090 |
| **Grafana** | Visualização de métricas e logs | 3000 | http://localhost:3000 |
| **Loki** | Agregação de logs | 3100 | http://localhost:3100 |
| **OTel Collector** | Recebe traces e métricas | 4317/4318 | - |

## Estrutura de Diretórios

```
deploy/observability/
├── namespace.yaml
├── prometheus-configmap.yaml
├── prometheus-rules-configmap.yaml
├── prometheus-rbac.yaml
├── prometheus-deployment.yaml
├── grafana-configmap.yaml
├── grafana-pvc.yaml
├── grafana-deployment.yaml
├── loki-configmap.yaml
├── loki-deployment.yaml
├── otel-configmap.yaml
└── otel-collector.yaml
```

## 1. Prometheus

### 1.1. Configuração

O Prometheus é configurado via ConfigMap com um `prometheus.yml` que define os jobs de coleta:

```yaml
scrape_configs:
  - job_name: 'jc-kubescale-api'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - jc-kubescale
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

### 1.2. RBAC

O Prometheus precisa de permissões para descobrir pods no cluster. Isso é feito via:

- **ServiceAccount:** `prometheus`
- **ClusterRole:** `prometheus` (get, list, watch em pods, services, endpoints, nodes)
- **ClusterRoleBinding:** `prometheus`

### 1.3. Annotations nos Pods

Para que o Prometheus descubra um pod, ele precisa ter as seguintes annotations:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"
```

### 1.4. Métricas Coletadas

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `http_requests_total` | Counter | Total de requisições HTTP |
| `http_request_latency_seconds` | Histogram | Latência das requisições |
| `http_active_requests` | Gauge | Requisições ativas |
| `tokens_input_total` | Counter | Total de tokens de entrada |
| `tokens_output_total` | Counter | Total de tokens de saída |

### 1.5. Alertas

Regras de alerta configuradas:

| Alerta | Condição | Severidade |
|--------|----------|------------|
| `APIDown` | `up{job="jc-kubescale-api"} == 0` | critical |
| `HighLatency` | `histogram_quantile(0.95, ...) > 2` | warning |
| `HighErrorRate` | `rate(...) > 0.05` | critical |

## 2. Grafana

### 2.1. Configuração

O Grafana é configurado via ConfigMaps:

- **Datasources:** Prometheus, Loki, Tempo
- **Dashboards:** Dashboards provisionados automaticamente

### 2.2. Persistência

O Grafana usa PVC para persistir:

- `grafana.db` (banco de dados SQLite)
- Configurações de usuário
- API keys
- Preferências

### 2.3. Datasources

| Nome | Tipo | URL |
|------|------|-----|
| Prometheus | prometheus | http://prometheus-server.observability.svc.cluster.local:80 |
| Loki | loki | http://loki.observability.svc.cluster.local:3100 |
| Tempo | tempo | http://tempo.observability.svc.cluster.local:3100 |

### 2.4. Dashboards

Dashboards provisionados:

- **JC-KubeScale AI - Overview:** Requests/s, P95 Latency, Active Requests, Error Rate, Tokens/s, Pod Status

## 3. Loki

### 3.1. Configuração

O Loki é configurado via ConfigMap com schema v13 e TSDB:

```yaml
schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
```

### 3.2. API

| Endpoint | Descrição |
|----------|-----------|
| `/ready` | Readiness probe |
| `/metrics` | Métricas Prometheus |
| `/loki/api/v1/query` | Consulta de logs |
| `/loki/api/v1/labels` | Lista de labels |

### 3.3. Acesso

O Loki não possui interface web. Os logs são visualizados através do **Grafana Explore**.

## 4. OpenTelemetry Collector

### 4.1. Configuração

O OTel Collector recebe traces da API via OTLP:

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  debug:
    verbosity: detailed
```

### 4.2. Pipelines

| Pipeline | Receivers | Processors | Exporters |
|----------|-----------|------------|-----------|
| traces | otlp | memory_limiter, batch | debug |
| metrics | otlp | memory_limiter, batch | debug |
| logs | otlp | memory_limiter, batch | debug |

## 5. Comandos de Operação

### 5.1. Deploy

```bash
# Deploy completo da observabilidade
make deploy-observability

# Verificar status
make status-observability

# Ver logs
make logs-observability
```

### 5.2. Port-Forward

```bash
# Iniciar todos os port-forwards
make port-forward-all

# Parar todos
make port-forward-stop

# Apenas Grafana
make port-forward-grafana

# Apenas Prometheus
make port-forward-prometheus

# Apenas Loki
make port-forward-loki
```

### 5.3. Undeploy

```bash
# Remover deployments (preserva PVC)
make undeploy-observability

# Remover tudo (inclui PVC)
make undeploy-observability-clean
```

### 5.4. Backup

```bash
# Backup do grafana.db
make backup-grafana
```

## 6. Acessos

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |

## 7. Validação

### 7.1. Verificar Prometheus

```bash
# Verificar targets
curl -s http://localhost:9090/api/v1/targets | python3 -c "
import json, sys
data = json.load(sys.stdin)
targets = data.get('data', {}).get('activeTargets', [])
print(f'Total de targets: {len(targets)}')
for t in targets:
    print(f\"  Job: {t.get('labels', {}).get('job', 'N/A')}\")
    print(f\"  Health: {t.get('health', 'N/A')}\")
    print(f\"  URL: {t.get('scrapeUrl', 'N/A')}\")
"

# Consultar métricas
curl -s "http://localhost:9090/api/v1/query?query=http_requests_total" | python3 -m json.tool
```

### 7.2. Verificar Loki

```bash
# Verificar readiness
curl -s http://localhost:3100/ready

# Listar labels
curl -s http://localhost:3100/loki/api/v1/labels

# Consultar logs
curl -s "http://localhost:3100/loki/api/v1/query_range?query={namespace=\"jc-kubescale\"}&limit=10" | python3 -m json.tool
```

### 7.3. Verificar Grafana

```bash
# Verificar health
curl -s http://localhost:3000/api/health | python3 -m json.tool

# Listar datasources
curl -s -u admin:admin http://localhost:3000/api/datasources | python3 -m json.tool
```

### 7.4. Verificar OTel Collector

```bash
# Verificar logs
kubectl logs -n observability -l app=otel-collector --tail=20
```

## 8. Troubleshooting

### 8.1. Prometheus não descobre pods

**Sintoma:** `activeTargets: []`

**Causa:** RBAC não configurado ou annotations ausentes.

**Solução:**

```bash
# Verificar RBAC
kubectl get serviceaccount prometheus -n observability
kubectl get clusterrole prometheus
kubectl get clusterrolebinding prometheus

# Verificar annotations do pod
kubectl get pod -n jc-kubescale -l app=jc-kubescale-api -o jsonpath='{.items[0].metadata.annotations}'
```

### 8.2. Loki em CrashLoopBackOff

**Sintoma:** Pod do Loki reiniciando constantemente.

**Causas:**

| Erro | Solução |
|------|---------|
| `field max_entries_limit not found` | Usar `max_entries_limit_per_query` |
| `schema v13 is required` | Atualizar schema para v13 e usar TSDB |
| `logging exporter has been deprecated` | Usar exporter `debug` |

### 8.3. Grafana sem dados

**Sintoma:** Dashboards vazios.

**Causas:**

| Causa | Solução |
|-------|---------|
| Datasource incorreto | Verificar URL do Prometheus no Grafana |
| Prometheus sem dados | Verificar targets e RBAC |
| Query incorreta | Verificar expressão no Grafana Explore |

### 8.4. PVC em Pending

**Sintoma:** `grafana-pvc` em `Pending`.

**Causa:** StorageClass não existe ou não tem provisioner.

**Solução:**

```bash
# Verificar StorageClasses
kubectl get storageclass

# Instalar local-path-provisioner (já vem no Kind)
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
```

## 9. Boas Práticas

### 9.1. Annotations Obrigatórias

Todo pod que deve ser monitorado precisa das annotations:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
  prometheus.io/path: "/metrics"
```

### 9.2. GitOps

Dashboards e datasources devem ser versionados no Git via ConfigMap. Configurações manuais devem ser evitadas.

### 9.3. Persistência

O PVC do Grafana preserva dados entre reinicializações. Use `make undeploy-observability` (não `clean`) para preservar.

### 9.4. Segurança

- Credenciais do Grafana devem ser alteradas em produção
- TLS deve ser configurado para endpoints expostos
- RBAC deve seguir o princípio do menor privilégio

## 10. Próximos Passos

- [ ] Configurar alertas no Alertmanager
- [ ] Adicionar dashboards para Loki
- [ ] Configurar Tempo para traces
- [ ] Implementar retenção de métricas
- [ ] Configurar backup automatizado do Grafana
- [ ] Migrar para PostgreSQL em produção

## 11. Referências

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
