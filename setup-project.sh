#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=============================================="
echo " JC-KubeScale AI - Project Structure Setup"
echo "=============================================="
echo
echo "Diretório: ${PROJECT_ROOT}"
echo

# ============================================
# Diretórios
# ============================================

DIRECTORIES=(
    "charts/jc-kubescale/templates"

    "deploy/base"
    "deploy/dev/patches"
    "deploy/kind"

    "infrastructure/kind"

    "services/api/src/app/api"
    "services/api/src/app/core"
    "services/api/src/app/services"
    "services/api/src/app/models"
    "services/api/src/tests"

    "tests/unit"
    "tests/integration"
    "tests/load"
    "tests/chaos"

    ".github/workflows"

    "docs"
)

echo "[1/3] Criando diretórios..."

for dir in "${DIRECTORIES[@]}"; do
    mkdir -p "${PROJECT_ROOT}/${dir}"
    echo "  + ${dir}"
done

echo

# ============================================
# Arquivos
# ============================================

FILES=(
    "Makefile"
    ".dockerignore"

    "go.mod"
    "go.sum"

    "charts/jc-kubescale/Chart.yaml"
    "charts/jc-kubescale/values.yaml"
    "charts/jc-kubescale/values-dev.yaml"
    "charts/jc-kubescale/templates/_helpers.tpl"
    "charts/jc-kubescale/templates/deployment.yaml"
    "charts/jc-kubescale/templates/service.yaml"
    "charts/jc-kubescale/templates/configmap.yaml"
    "charts/jc-kubescale/templates/secrets.yaml"
    "charts/jc-kubescale/templates/ingress.yaml"
    "charts/jc-kubescale/templates/hpa.yaml"
    "charts/jc-kubescale/README.md"

    "deploy/base/namespace.yaml"
    "deploy/base/api-deployment.yaml"
    "deploy/base/api-service.yaml"
    "deploy/base/api-configmap.yaml"
    "deploy/dev/kustomization.yaml"
    "deploy/kind/kind-config.yaml"

    "infrastructure/kind/kind-config.yaml"

    "services/api/Dockerfile"
    "services/api/Dockerfile.dev"
    "services/api/requirements.txt"
    "services/api/pyproject.toml"

    "services/api/src/__init__.py"
    "services/api/src/main.py"

    "services/api/src/app/__init__.py"

    "services/api/src/app/api/__init__.py"
    "services/api/src/app/api/routes.py"
    "services/api/src/app/api/models.py"
    "services/api/src/app/api/dependencies.py"

    "services/api/src/app/core/__init__.py"
    "services/api/src/app/core/config.py"
    "services/api/src/app/core/logging.py"
    "services/api/src/app/core/exceptions.py"

    "services/api/src/app/services/__init__.py"
    "services/api/src/app/services/inference.py"

    "services/api/src/app/models/__init__.py"
    "services/api/src/app/models/schemas.py"

    "services/api/src/tests/__init__.py"
    "services/api/src/tests/test_health.py"
    "services/api/src/tests/test_chat.py"

    ".github/workflows/ci.yaml"
    ".github/workflows/security.yaml"
    ".github/workflows/release.yaml"

    "docs/architecture.md"
)

echo "[2/3] Criando arquivos..."

for file in "${FILES[@]}"; do
    filepath="${PROJECT_ROOT}/${file}"

    if [[ ! -e "${filepath}" ]]; then
        touch "${filepath}"
        echo "  + ${file}"
    else
        echo "  = ${file} (já existe, preservado)"
    fi
done

echo

# ============================================
# .gitkeep para diretórios inicialmente vazios
# ============================================

GITKEEP_FILES=(
    "deploy/dev/patches/.gitkeep"
    "tests/unit/.gitkeep"
    "tests/integration/.gitkeep"
    "tests/load/.gitkeep"
    "tests/chaos/.gitkeep"
)

echo "[3/3] Criando .gitkeep para diretórios vazios..."

for file in "${GITKEEP_FILES[@]}"; do
    filepath="${PROJECT_ROOT}/${file}"

    if [[ ! -e "${filepath}" ]]; then
        touch "${filepath}"
        echo "  + ${file}"
    else
        echo "  = ${file} (já existe)"
    fi
done

echo
echo "=============================================="
echo " Estrutura criada com sucesso!"
echo "=============================================="
echo
echo "Próximos passos:"
echo
echo "  1. Verificar estrutura:"
echo "     tree -a -I '.git'"
echo
echo "  2. Verificar Git:"
echo "     git status"
echo
echo "  3. Adicionar arquivos:"
echo "     git add ."
echo
echo "  4. Criar commit:"
echo "     git commit -m \"chore: initialize project structure\""
echo
