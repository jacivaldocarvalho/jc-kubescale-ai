.PHONY: help check-deps cluster cluster-delete install build load-image deploy deploy-clean undeploy test test-api logs status clean install-python-deps restart all deploy-observability undeploy-observability undeploy-observability-clean status-observability logs-observability backup-grafana port-forward-all port-forward-stop port-forward-grafana port-forward-prometheus port-forward-loki

SHELL := /bin/bash
KUBECONFIG := $(HOME)/.kube/config

NAMESPACE := jc-kubescale
OBS_NAMESPACE := observability

GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m


# ============================================
# HELP
# ============================================

help:
	@echo "JC-KubeScale AI Makefile"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-25s$(NC) %s\n", $$1, $$2}'


# ============================================
# DEPENDÊNCIAS
# ============================================

check-deps:
	@echo "$(GREEN)Verificando dependencias...$(NC)"
	@command -v kind >/dev/null 2>&1 || { echo "$(RED)kind nao encontrado. Execute: ./scripts/setup.sh$(NC)"; exit 1; }
	@command -v kubectl >/dev/null 2>&1 || { echo "$(RED)kubectl nao encontrado. Execute: ./scripts/setup.sh$(NC)"; exit 1; }
	@command -v helm >/dev/null 2>&1 || { echo "$(RED)helm nao encontrado. Execute: ./scripts/setup.sh$(NC)"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)docker nao encontrado.$(NC)"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)python3 nao encontrado.$(NC)"; exit 1; }
	@echo "$(GREEN)Todas as dependencias estao instaladas$(NC)"


# ============================================
# CLUSTER KIND
# ============================================

cluster: check-deps
	@echo "$(GREEN)Criando cluster Kind...$(NC)"
	@kind delete cluster --name jc-kubescale 2>/dev/null || true
	@kind create cluster --name jc-kubescale --config infrastructure/kind/kind-config.yaml
	@kubectl config use-context kind-jc-kubescale
	@echo "$(GREEN)Cluster criado.$(NC)"
	@kubectl get nodes
	@kubectl cluster-info

cluster-delete:
	@kind delete cluster --name jc-kubescale || true


# ============================================
# INSTALAÇÃO
# ============================================

install: check-deps
	@echo "$(GREEN)Instalando dependencias...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
	@helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
	@helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
	@helm repo update 2>/dev/null || true
	@echo "$(GREEN)Dependencias instaladas$(NC)"


# ============================================
# BUILD
# ============================================

build:
	@echo "$(GREEN)Buildando imagem Docker...$(NC)"
	@docker build -t jc-kubescale-api:latest -f services/api/Dockerfile services/api/
	@echo "$(GREEN)Imagem buildada: jc-kubescale-api:latest$(NC)"

load-image: build
	@echo "$(GREEN)Carregando imagem no Kind...$(NC)"
	@kind load docker-image jc-kubescale-api:latest --name jc-kubescale 2>/dev/null || true
	@echo "$(GREEN)Imagem carregada$(NC)"


# ============================================
# DEPLOY DA API
# ============================================

deploy-clean:
	@echo "$(GREEN)Removendo deploy anterior...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl delete deployment jc-kubescale-api -n $(NAMESPACE) 2>/dev/null || true
	@kubectl delete service jc-kubescale-api -n $(NAMESPACE) 2>/dev/null || true
	@sleep 3

deploy: check-deps build load-image deploy-clean
	@echo "$(GREEN)Deploy da plataforma...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
	@echo "$(GREEN)Aplicando manifests...$(NC)"
	@kubectl apply -f deploy/base/namespace.yaml
	@kubectl apply -f deploy/base/api-deployment.yaml
	@kubectl apply -f deploy/base/api-service.yaml
	@echo "$(GREEN)Aguardando pods...$(NC)"
	@kubectl wait --for=condition=ready pod -l app=jc-kubescale-api -n $(NAMESPACE) --timeout=120s 2>/dev/null || true
	@echo "$(GREEN)Deploy concluido!$(NC)"
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)API disponivel em: http://localhost:8080$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(GREEN)Teste:$(NC)"
	@curl -s http://localhost:8080/health 2>/dev/null | python3 -m json.tool || echo "$(YELLOW)Aguardando pod ficar pronto...$(NC)"

undeploy:
	@echo "$(GREEN)Removendo deploy...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl delete -f deploy/base/ 2>/dev/null || true
	@kubectl delete namespace $(NAMESPACE) 2>/dev/null || true
	@pkill -f "kubectl port-forward.*8080" 2>/dev/null || true


# ============================================
# TESTES
# ============================================

test:
	@echo "$(GREEN)Executando testes...$(NC)"
	@cd services/api && python3 -m pytest src/tests/ -v 2>/dev/null || echo "$(YELLOW)pytest nao instalado. Execute: make install-python-deps$(NC)"
	@echo "$(GREEN)Testes concluidos$(NC)"

test-api:
	@echo "$(GREEN)Testando API...$(NC)"
	@echo "$(YELLOW)Health check:$(NC)"
	@curl -s http://localhost:8080/health 2>/dev/null | python3 -m json.tool || echo "$(RED)API nao disponivel. Execute: make deploy$(NC)"
	@echo ""
	@echo "$(YELLOW)Listar modelos:$(NC)"
	@curl -s http://localhost:8080/v1/models 2>/dev/null | python3 -m json.tool || echo "$(RED)API nao disponivel$(NC)"
	@echo ""
	@echo "$(YELLOW)Chat:$(NC)"
	@curl -s -X POST http://localhost:8080/v1/chat \
		-H "Content-Type: application/json" \
		-d '{"message":"O que e Kubernetes?"}' 2>/dev/null | python3 -m json.tool || echo "$(RED)API nao disponivel$(NC)"


# ============================================
# LOGS / STATUS
# ============================================

logs:
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl logs -n $(NAMESPACE) -l app=jc-kubescale-api --tail=100 -f 2>/dev/null

status:
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@echo "$(GREEN)=== Recursos no namespace $(NAMESPACE) ===$(NC)"
	@kubectl get all -n $(NAMESPACE)
	@echo ""
	@echo "$(GREEN)=== Pods ===$(NC)"
	@kubectl get pods -n $(NAMESPACE)
	@echo ""
	@echo "$(GREEN)=== Services ===$(NC)"
	@kubectl get svc -n $(NAMESPACE)


# ============================================
# LIMPEZA
# ============================================

clean:
	@make cluster-delete
	@docker rmi jc-kubescale-api:latest 2>/dev/null || true
	@pkill -f "kubectl port-forward" 2>/dev/null || true
	@echo "$(GREEN)Limpeza concluida$(NC)"


# ============================================
# PYTHON
# ============================================

install-python-deps:
	@echo "$(GREEN)Instalando dependencias Python...$(NC)"
	@cd services/api && pip install -r requirements.txt
	@cd services/api && pip install pytest pytest-asyncio pytest-cov
	@echo "$(GREEN)Dependencias Python instaladas$(NC)"


# ============================================
# RESTART
# ============================================

restart:
	@echo "$(GREEN)Reiniciando pods...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl rollout restart deployment jc-kubescale-api -n $(NAMESPACE)
	@kubectl wait --for=condition=ready pod -l app=jc-kubescale-api -n $(NAMESPACE) --timeout=120s 2>/dev/null || true
	@echo "$(GREEN)Reinicio concluido$(NC)"


# ============================================
# ALL
# ============================================

all: check-deps cluster install build load-image deploy-clean deploy test-api
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)JC-KubeScale AI pronto!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)API: http://localhost:8080$(NC)"
	@echo "$(GREEN)Health: http://localhost:8080/health$(NC)"
	@echo "$(GREEN)Models: http://localhost:8080/v1/models$(NC)"
	@echo "$(GREEN)Chat: curl -X POST http://localhost:8080/v1/chat -H 'Content-Type: application/json' -d '{\"message\":\"Teste\"}'$(NC)"


# ============================================
# OBSERVABILIDADE
# ============================================

deploy-observability:
	@echo "$(GREEN)Deploy da observabilidade...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl create namespace $(OBS_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
	@echo "$(GREEN)Aplicando ConfigMaps...$(NC)"
	@kubectl apply -f deploy/observability/prometheus-configmap.yaml
	@kubectl apply -f deploy/observability/prometheus-rules-configmap.yaml
	@kubectl apply -f deploy/observability/grafana-configmap.yaml
	@kubectl apply -f deploy/observability/loki-configmap.yaml
	@kubectl apply -f deploy/observability/otel-configmap.yaml
	@echo "$(GREEN)Aplicando RBAC...$(NC)"
	@kubectl apply -f deploy/observability/prometheus-rbac.yaml
	@echo "$(GREEN)Aplicando PVC...$(NC)"
	@kubectl apply -f deploy/observability/grafana-pvc.yaml
	@echo "$(GREEN)Aplicando Deployments...$(NC)"
	@kubectl apply -f deploy/observability/prometheus-deployment.yaml
	@kubectl apply -f deploy/observability/grafana-deployment.yaml
	@kubectl apply -f deploy/observability/loki-deployment.yaml
	@kubectl apply -f deploy/observability/otel-collector.yaml
	@echo "$(GREEN)Aguardando pods...$(NC)"
	@kubectl wait --for=condition=ready pod -l app=prometheus -n $(OBS_NAMESPACE) --timeout=180s 2>/dev/null || true
	@kubectl wait --for=condition=ready pod -l app=grafana -n $(OBS_NAMESPACE) --timeout=180s 2>/dev/null || true
	@kubectl wait --for=condition=ready pod -l app=loki -n $(OBS_NAMESPACE) --timeout=180s 2>/dev/null || true
	@kubectl wait --for=condition=ready pod -l app=otel-collector -n $(OBS_NAMESPACE) --timeout=180s 2>/dev/null || true
	@echo "$(GREEN)Observabilidade deployada!$(NC)"
	@$(MAKE) port-forward-all


# ============================================
# UNDEPLOY OBSERVABILIDADE
# Mantém os PVCs / dados do Grafana
# ============================================

undeploy-observability:
	@echo "$(GREEN)Removendo observabilidade (dados preservados)...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@echo "$(YELLOW)Removendo Deployments e Services...$(NC)"
	@kubectl delete deployment -n $(OBS_NAMESPACE) --all 2>/dev/null || true
	@kubectl delete service -n $(OBS_NAMESPACE) --all 2>/dev/null || true
	@kubectl delete configmap -n $(OBS_NAMESPACE) --all 2>/dev/null || true
	@echo "$(YELLOW)PVCs preservados (dados do Grafana):$(NC)"
	@kubectl get pvc -n $(OBS_NAMESPACE)
	@$(MAKE) port-forward-stop
	@echo "$(GREEN)Observabilidade removida (dados preservados)$(NC)"
	@echo "$(YELLOW)Para remover os dados: make undeploy-observability-clean$(NC)"


# ============================================
# UNDEPLOY COMPLETO
# Remove namespace + PVCs + dados
# ============================================

undeploy-observability-clean:
	@echo "$(RED)Removendo observabilidade COMPLETAMENTE (incluindo dados)...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl delete namespace $(OBS_NAMESPACE) 2>/dev/null || true
	@$(MAKE) port-forward-stop
	@echo "$(GREEN)Observabilidade removida completamente$(NC)"


# ============================================
# PORT FORWARDS
# ============================================

port-forward-all:
	@echo "$(GREEN)Iniciando port-forwards em background...$(NC)"
	-@pkill -f "kubectl port-forward.*observability" 2>/dev/null || true
	@sleep 1
	-@nohup kubectl port-forward -n $(OBS_NAMESPACE) svc/grafana 3000:80 > /tmp/pf-grafana.log 2>&1 &
	-@nohup kubectl port-forward -n $(OBS_NAMESPACE) svc/prometheus-server 9090:80 > /tmp/pf-prometheus.log 2>&1 &
	-@nohup kubectl port-forward -n $(OBS_NAMESPACE) svc/loki 3100:3100 > /tmp/pf-loki.log 2>&1 &
	@sleep 3
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Observabilidade disponivel:$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)Grafana:    http://localhost:3000 (admin/admin)$(NC)"
	@echo "$(GREEN)Prometheus: http://localhost:9090$(NC)"
	@echo "$(GREEN)Loki:       http://localhost:3100$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Para parar: make port-forward-stop$(NC)"

port-forward-stop:
	@echo "$(GREEN)Parando port-forwards...$(NC)"
	@pkill -f "kubectl port-forward.*observability" 2>/dev/null || true
	@pkill -f "kubectl port-forward.*grafana" 2>/dev/null || true
	@pkill -f "kubectl port-forward.*prometheus" 2>/dev/null || true
	@pkill -f "kubectl port-forward.*loki" 2>/dev/null || true
	@echo "$(GREEN)Port-forwards encerrados$(NC)"

port-forward-grafana:
	@echo "$(GREEN)Iniciando port-forward do Grafana...$(NC)"
	@nohup kubectl port-forward -n $(OBS_NAMESPACE) svc/grafana 3000:80 > /tmp/pf-grafana.log 2>&1 &
	@sleep 2
	@echo "$(GREEN)Grafana: http://localhost:3000 (admin/admin)$(NC)"

port-forward-prometheus:
	@echo "$(GREEN)Iniciando port-forward do Prometheus...$(NC)"
	@nohup kubectl port-forward -n $(OBS_NAMESPACE) svc/prometheus-server 9090:80 > /tmp/pf-prometheus.log 2>&1 &
	@sleep 2
	@echo "$(GREEN)Prometheus: http://localhost:9090$(NC)"

port-forward-loki:
	@echo "$(GREEN)Iniciando port-forward do Loki...$(NC)"
	@nohup kubectl port-forward -n $(OBS_NAMESPACE) svc/loki 3100:3100 > /tmp/pf-loki.log 2>&1 &
	@sleep 2
	@echo "$(GREEN)Loki: http://localhost:3100$(NC)"


# ============================================
# STATUS OBSERVABILIDADE
# ============================================

status-observability:
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@echo "$(GREEN)=== Recursos no namespace $(OBS_NAMESPACE) ===$(NC)"
	@kubectl get all -n $(OBS_NAMESPACE)
	@echo ""
	@echo "$(GREEN)=== PVCs ===$(NC)"
	@kubectl get pvc -n $(OBS_NAMESPACE)
	@echo ""
	@echo "$(GREEN)=== Port-forwards ativos ===$(NC)"
	@ps aux | grep "kubectl port-forward" | grep -v grep || echo "$(YELLOW)Nenhum port-forward ativo$(NC)"


# ============================================
# LOGS OBSERVABILIDADE
# ============================================

logs-observability:
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@echo "$(GREEN)Logs do Prometheus:$(NC)"
	@kubectl logs -n $(OBS_NAMESPACE) -l app=prometheus --tail=20
	@echo ""
	@echo "$(GREEN)Logs do Grafana:$(NC)"
	@kubectl logs -n $(OBS_NAMESPACE) -l app=grafana --tail=20
	@echo ""
	@echo "$(GREEN)Logs do Loki:$(NC)"
	@kubectl logs -n $(OBS_NAMESPACE) -l app=loki --tail=20
	@echo ""
	@echo "$(GREEN)Logs do OTel Collector:$(NC)"
	@kubectl logs -n $(OBS_NAMESPACE) -l app=otel-collector --tail=20


# ============================================
# BACKUP GRAFANA
# ============================================

backup-grafana:
	@echo "$(GREEN)Fazendo backup do Grafana...$(NC)"
	@mkdir -p ./backups
	@kubectl exec -n $(OBS_NAMESPACE) deployment/grafana -- \
		cat /var/lib/grafana/grafana.db > ./backups/grafana-$$(date +%Y%m%d-%H%M%S).db
	@echo "$(GREEN)Backup salvo em ./backups/$(NC)"
	@ls -lh ./backups/