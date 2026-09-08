#!/bin/bash
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${GREEN}JC-KubeScale AI - Setup Automático${NC}"
echo ""

# Detecta sistema operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*|MINGW*|MSYS*) MACHINE=Windows;;
    *)          MACHINE="UNKNOWN";;
esac

echo -e "${GREEN}Sistema detectado: ${MACHINE}${NC}"

# Funcao para verificar e instalar
install_if_missing() {
    local cmd=$1
    local install_cmd=$2
    if ! command -v $cmd &> /dev/null; then
        echo -e "${YELLOW}Instalando $cmd...${NC}"
        eval $install_cmd
    else
        echo -e "${GREEN}$cmd já instalado${NC}"
    fi
}

# Instala ferramentas base
if [ "$MACHINE" == "Linux" ]; then
    echo -e "${GREEN}Instalando dependencias para Linux...${NC}"
    
    # Kind
    install_if_missing kind "curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind"
    
    # Kubectl
    install_if_missing kubectl "curl -LO https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl && chmod +x ./kubectl && sudo mv ./kubectl /usr/local/bin/kubectl"
    
    # Helm
    install_if_missing helm "curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
    
    # Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker não encontrado. Instale manualmente: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    # Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python3 não encontrado. Instale manualmente.${NC}"
        exit 1
    fi
    
elif [ "$MACHINE" == "Mac" ]; then
    echo -e "${GREEN}Instalando dependencias para macOS...${NC}"
    
    # Homebrew
    if ! command -v brew &> /dev/null; then
        echo -e "${YELLOW}Instalando Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    install_if_missing kind "brew install kind"
    install_if_missing kubectl "brew install kubectl"
    install_if_missing helm "brew install helm"
    install_if_missing docker "brew install docker"
    install_if_missing python3 "brew install python"
    install_if_missing k6 "brew install k6"
else
    echo -e "${RED}Sistema não suportado para instalação automática. Instale manualmente:${NC}"
    echo "  - kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    echo "  - kubectl: https://kubernetes.io/docs/tasks/tools/"
    echo "  - helm: https://helm.sh/docs/intro/install/"
    echo "  - docker: https://docs.docker.com/get-docker/"
    echo "  - python3: https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}Setup concluido!${NC}"
echo ""
echo -e "${GREEN}Proximo passo:${NC}"
echo "  make cluster"
echo "  make install"
echo "  make deploy"