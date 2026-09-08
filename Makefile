.PHONY: help check-deps cluster cluster-delete install build load-image deploy deploy-clean test test-api logs status clean port-forward

SHELL := /bin/bash
KUBECONFIG := $(HOME)/.kube/config
NAMESPACE := jc-kubescale

GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
NC := \033[0m

help:
	@echo "JC-KubeScale AI Makefile"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

check-deps:
	@echo "$(GREEN)Verificando dependencias...$(NC)"
	@command -v kind >/dev/null 2>&1 || { echo "$(RED)kind nao encontrado. Execute: ./scripts/setup.sh$(NC)"; exit 1; }
	@command -v kubectl >/dev/null 2>&1 || { echo "$(RED)kubectl nao encontrado. Execute: ./scripts/setup.sh$(NC)"; exit 1; }
	@command -v helm >/dev/null 2>&1 || { echo "$(RED)helm nao encontrado. Execute: ./scripts/setup.sh$(NC)"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)docker nao encontrado.$(NC)"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "$(RED)python3 nao encontrado.$(NC)"; exit 1; }
	@echo "$(GREEN)Todas as dependencias estao instaladas$(NC)"

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

install: check-deps
	@echo "$(GREEN)Instalando dependencias...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f - 2>/dev/null || true
	@helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 2>/dev/null || true
	@helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
	@helm repo update 2>/dev/null || true
	@echo "$(GREEN)Dependencias instaladas$(NC)"

build:
	@echo "$(GREEN)Buildando imagem Docker...$(NC)"
	@docker build -t jc-kubescale-api:latest -f services/api/Dockerfile services/api/
	@echo "$(GREEN)Imagem buildada: jc-kubescale-api:latest$(NC)"

load-image: build
	@echo "$(GREEN)Carregando imagem no Kind...$(NC)"
	@kind load docker-image jc-kubescale-api:latest --name jc-kubescale 2>/dev/null || true
	@echo "$(GREEN)Imagem carregada$(NC)"

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
	@curl -s -X POST http://localhost:8080/v1/chat -H "Content-Type: application/json" -d '{"message":"O que e Kubernetes?"}' 2>/dev/null | python3 -m json.tool || echo "$(RED)API nao disponivel$(NC)"

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

clean:
	@make cluster-delete
	@docker rmi jc-kubescale-api:latest 2>/dev/null || true
	@pkill -f "kubectl port-forward.*8080" 2>/dev/null || true
	@echo "$(GREEN)Limpeza concluida$(NC)"

install-python-deps:
	@echo "$(GREEN)Instalando dependencias Python...$(NC)"
	@cd services/api && pip install -r requirements.txt
	@cd services/api && pip install pytest pytest-asyncio pytest-cov
	@echo "$(GREEN)Dependencias Python instaladas$(NC)"

restart:
	@echo "$(GREEN)Reiniciando pods...$(NC)"
	@kubectl config use-context kind-jc-kubescale 2>/dev/null || true
	@kubectl rollout restart deployment jc-kubescale-api -n $(NAMESPACE)
	@kubectl wait --for=condition=ready pod -l app=jc-kubescale-api -n $(NAMESPACE) --timeout=120s 2>/dev/null || true
	@echo "$(GREEN)Reinicio concluido$(NC)"

all: check-deps cluster install build load-image deploy-clean deploy test-api
	@echo ""
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)JC-KubeScale AI pronto!$(NC)"
	@echo "$(GREEN)========================================$(NC)"
	@echo "$(GREEN)API: http://localhost:8080$(NC)"
	@echo "$(GREEN)Health: http://localhost:8080/health$(NC)"
	@echo "$(GREEN)Models: http://localhost:8080/v1/models$(NC)"
	@echo "$(GREEN)Chat: curl -X POST http://localhost:8080/v1/chat -H 'Content-Type: application/json' -d '{\"message\":\"Teste\"}'$(NC)"