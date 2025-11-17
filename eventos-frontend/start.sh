#!/bin/bash

# ============================================
# SCRIPT DE INICIALIZAÇÃO - SISTEMA DE EVENTOS
# ============================================
# 
# Este script ajuda a iniciar todo o sistema
# de forma organizada.
#
# Uso:
#   chmod +x start.sh
#   ./start.sh
#
# ============================================

set -e  # Parar se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para print colorido
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   SISTEMA DE EVENTOS - INICIALIZAÇÃO   ║"
echo "╔════════════════════════════════════════╗"
echo ""

# 1. Verificar Node.js
print_info "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    print_error "Node.js não encontrado. Por favor, instale Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v)
print_success "Node.js instalado: $NODE_VERSION"

# 2. Verificar se estamos no diretório correto
print_info "Verificando estrutura do projeto..."
if [ ! -f "package.json" ]; then
    print_error "package.json não encontrado. Execute este script na raiz do projeto Next.js"
    exit 1
fi
print_success "Estrutura do projeto OK"

# 3. Verificar .env.local
print_info "Verificando arquivo de configuração..."
if [ ! -f ".env.local" ]; then
    print_warning "Arquivo .env.local não encontrado"
    
    if [ -f ".env.example" ]; then
        print_info "Copiando .env.example para .env.local..."
        cp .env.example .env.local
        print_warning "ATENÇÃO: Edite .env.local com suas configurações antes de continuar!"
        print_info "Execute: nano .env.local"
        exit 1
    else
        print_error "Nem .env.local nem .env.example encontrados"
        print_info "Crie um arquivo .env.local com as variáveis necessárias"
        exit 1
    fi
else
    print_success "Arquivo .env.local encontrado"
fi

# 4. Verificar se as dependências estão instaladas
print_info "Verificando dependências..."
if [ ! -d "node_modules" ]; then
    print_warning "node_modules não encontrado"
    print_info "Instalando dependências..."
    npm install
    print_success "Dependências instaladas"
else
    print_success "Dependências já instaladas"
fi

# 5. Verificar se os microsserviços estão rodando
print_info "Verificando microsserviços..."

# Extrair URLs do .env.local
if command -v grep &> /dev/null; then
    AUTH_URL=$(grep NEXT_PUBLIC_AUTH_URL .env.local | cut -d '=' -f2)
    
    if [ ! -z "$AUTH_URL" ]; then
        print_info "Testando conexão com Auth Service ($AUTH_URL)..."
        
        # Tentar fazer uma requisição simples
        if command -v curl &> /dev/null; then
            if curl -s -f -m 2 "$AUTH_URL" > /dev/null 2>&1 || \
               curl -s -f -m 2 "$AUTH_URL/docs" > /dev/null 2>&1; then
                print_success "Auth Service está respondendo"
            else
                print_warning "Auth Service não está respondendo em $AUTH_URL"
                print_info "Certifique-se de que todos os microsserviços estão rodando"
            fi
        else
            print_warning "curl não disponível, pulando teste de conexão"
        fi
    fi
fi

# 6. Perguntar modo de execução
echo ""
echo "Como você deseja executar o frontend?"
echo "1) Desenvolvimento (npm run dev)"
echo "2) Produção (npm run build && npm start)"
echo "3) Apenas verificar configuração"
echo ""
read -p "Escolha uma opção (1-3): " opcao

case $opcao in
    1)
        print_info "Iniciando em modo de desenvolvimento..."
        print_info "Acesse: http://localhost:3000"
        echo ""
        npm run dev
        ;;
    2)
        print_info "Fazendo build para produção..."
        npm run build
        
        if [ $? -eq 0 ]; then
            print_success "Build concluído com sucesso"
            print_info "Iniciando servidor de produção..."
            print_info "Acesse: http://localhost:3000"
            echo ""
            npm start
        else
            print_error "Erro no build"
            exit 1
        fi
        ;;
    3)
        print_success "Verificação concluída!"
        echo ""
        print_info "Para iniciar o frontend:"
        echo "  Desenvolvimento: npm run dev"
        echo "  Produção:       npm run build && npm start"
        echo ""
        print_info "Depois de iniciar, acesse: http://localhost:3000"
        ;;
    *)
        print_error "Opção inválida"
        exit 1
        ;;
esac

echo ""
print_success "Script finalizado!"
