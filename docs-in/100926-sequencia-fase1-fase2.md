# Teste Completo: Clean + Redeploy

## Sequência Recomendada

### Passo 1: Estado Atual (para referência)

Antes de limpar, capture o estado atual para comparação:

```bash
# Verificar cluster
kind get clusters

# Verificar nós
kubectl get nodes

# Verificar namespace jc-kubescale
kubectl get all -n jc-kubescale

# Verificar namespace observability
kubectl get all -n observability

# Verificar PVCs
kubectl get pvc -A

# Verificar port-forwards ativos
ps aux | grep "kubectl port-forward" | grep -v grep
```

### Passo 2: Clean Total

```bash
# Remove TODOS os port-forwards primeiro
make port-forward-stop

# Remove o cluster Kind inteiro
make clean
```

**O que `make clean` faz:**
1. Remove o cluster Kind
2. Remove a imagem Docker `jc-kubescale-api:latest`
3. Encerra todos os port-forwards

**Após o clean, verifique:**

```bash
# Não deve existir cluster
kind get clusters

# Não deve existir contexto
kubectl config get-contexts

# Não deve existir imagem
docker images | grep jc-kubescale
```

### Passo 3: Redeploy Completo

```bash
# Executa tudo do zero
make all
```

**O que `make all` faz:**

| Ordem | Comando | O que faz |
|-------|---------|-----------|
| 1 | `check-deps` | Verifica dependências |
| 2 | `cluster` | Cria cluster Kind |
| 3 | `install` | Instala repositórios Helm |
| 4 | `build` | Constrói imagem Docker |
| 5 | `load-image` | Carrega imagem no Kind |
| 6 | `deploy-clean` | Remove deploy anterior |
| 7 | `deploy` | Deploy da API |
| 8 | `test-api` | Testa endpoints |

**Saída esperada:**

```
========================================
JC-KubeScale AI pronto!
========================================
API: http://localhost:8080
Health: http://localhost:8080/health
Models: http://localhost:8080/v1/models
Chat: curl -X POST http://localhost:8080/v1/chat -H 'Content-Type: application/json' -d '{"message":"Teste"}'
```

### Passo 4: Deploy da Observabilidade

```bash
# Deploy da stack de observabilidade
make deploy-observability
```

**O que `make deploy-observability` faz:**

| Ordem | Ação | O que faz |
|-------|------|-----------|
| 1 | Namespace | Cria `observability` |
| 2 | ConfigMaps | Aplica configs do Prometheus, Grafana, Loki, OTel |
| 3 | PVC | Cria `grafana-pvc` |
| 4 | Deployments | Aplica Prometheus, Grafana, Loki, OTel |
| 5 | Aguarda | Espera pods ficarem prontos |
| 6 | Port-forward | Inicia port-forwards automaticamente |

### Passo 5: Verificação Completa

```bash
# Status da API
make status

# Status da observabilidade
make status-observability

# Testar API
make test-api

# Verificar PVCs
kubectl get pvc -n observability

# Verificar pods
kubectl get pods -n observability

# Verificar port-forwards
ps aux | grep "kubectl port-forward" | grep -v grep

# Testar acessos
curl -s http://localhost:8080/health
curl -s http://localhost:3000/api/health
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:3100/ready
```

## Checklist de Validação

### Após `make clean`

- [ ] Cluster Kind removido (`kind get clusters` vazio)
- [ ] Contexto kubectl removido
- [ ] Imagem Docker removida
- [ ] Port-forwards encerrados

### Após `make all`

- [ ] Cluster Kind criado (4 nós)
- [ ] Namespace `jc-kubescale` criado
- [ ] API rodando (`kubectl get pods -n jc-kubescale`)
- [ ] Service acessível em `http://localhost:8080`
- [ ] Health check respondendo
- [ ] Chat respondendo

### Após `make deploy-observability`

- [ ] Namespace `observability` criado
- [ ] 5 ConfigMaps criados
- [ ] PVC `grafana-pvc` criado
- [ ] 4 pods rodando (Prometheus, Grafana, Loki, OTel)
- [ ] 4 Services criados
- [ ] Port-forwards ativos
- [ ] Grafana acessível em `http://localhost:3000`
- [ ] Prometheus acessível em `http://localhost:9090`
- [ ] Loki acessível em `http://localhost:3100`

## Acessos Após o Redeploy

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API | http://localhost:8080 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Prometheus | http://localhost:9090 | - |
| Loki | http://localhost:3100 | - |

## Comandos de Diagnóstico (se algo falhar)

```bash
# Se algum pod não subir
kubectl describe pod -n observability -l app=<nome>
kubectl logs -n observability -l app=<nome>

# Se o PVC não for criado
kubectl get storageclass
kubectl describe pvc grafana-pvc -n observability

# Se o port-forward falhar
cat /tmp/pf-grafana.log
cat /tmp/pf-prometheus.log
cat /tmp/pf-loki.log

# Se a API não responder
kubectl logs -n jc-kubescale -l app=jc-kubescale-api
kubectl describe pod -n jc-kubescale -l app=jc-kubescale-api
```

## Tempo Estimado

| Etapa | Tempo |
|-------|-------|
| `make clean` | ~30s |
| `make all` | ~3-5min |
| `make deploy-observability` | ~2-3min |
| **Total** | **~6-9min** |

O tempo pode variar dependendo da velocidade da conexão (download de imagens Docker).

## Próximos Passos Após o Teste

1. **Validar acessos** - Verificar se todos os serviços estão acessíveis
2. **Importar dashboards** - Se necessário, importar dashboards no Grafana
3. **Verificar métricas** - Confirmar que o Prometheus está coletando métricas da API
4. **Verificar logs** - Confirmar que o Loki está recebendo logs
5. **Documentar** - Registrar o comportamento observado

## Observação Importante

Após `make clean` + `make all` + `make deploy-observability`:

- ✅ **Dashboards provisionados** (via ConfigMap) voltam automaticamente
- ❌ **Dashboards criados manualmente** são perdidos (não havia PVC antes)
- ✅ **PVC** é criado do zero
- ✅ **API** volta funcionando
- ✅ **Observabilidade** volta funcionando

Aguardo os logs da execução para analisar o comportamento completo do sistema.