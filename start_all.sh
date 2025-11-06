#!/bin/bash
# ============================================
# start_all.sh - VERSÃO CORRIGIDA
# Inicia todos os microsserviços
# ============================================

echo "🚀 Iniciando todos os microsserviços..."
echo ""

# Verificar se está no venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment não detectado!"
    if [ -d "venv" ]; then
        echo "   Ativando venv automaticamente..."
        source venv/bin/activate
    else
        echo "❌ Virtual environment não encontrado!"
        echo "   Execute: python3 -m venv venv"
        echo "   Depois: source venv/bin/activate"
        echo "   E: pip install -r requirements.txt"
        exit 1
    fi
fi

# Criar diretório de logs
mkdir -p logs

# Função para iniciar um serviço
start_service() {
    local service=$1
    local port=$2
    
    if [ ! -d "$service" ]; then
        echo "  ⚠️  ${service} não encontrado, pulando..."
        return
    fi
    
    if [ ! -f "${service}/main.py" ]; then
        echo "  ⚠️  ${service}/main.py não encontrado, pulando..."
        return
    fi
    
    echo "  ▶️  Iniciando ${service} na porta ${port}..."
    cd ${service}
    nohup python main.py > ../logs/${service}.log 2>&1 &
    echo $! > ../logs/${service}.pid
    cd ..
    sleep 1
}

# Iniciar todos os microsserviços
start_service "auth-service" "8001"
start_service "eventos-service" "8002"
start_service "usuarios-service" "8003"
start_service "inscricoes-service" "8004"
start_service "ingressos-service" "8005"
start_service "checkins-service" "8006"
start_service "certificados-service" "8007"

echo ""
echo "✅ Todos os serviços disponíveis foram iniciados!"
echo ""
echo "📊 Para verificar se estão rodando:"
echo "   bash status.sh"
echo ""
echo "📋 Para ver logs em tempo real:"
echo "   bash logs.sh auth"
echo "   bash logs.sh eventos"
echo ""
echo "⛔ Para parar todos:"
echo "   bash stop_all.sh"
echo ""
echo "🌐 Acessar documentação:"
echo "   http://localhost:8001/docs (Auth)"
echo "   http://localhost:8002/docs (Eventos)"
echo "   http://localhost:8003/docs (Usuários)"
