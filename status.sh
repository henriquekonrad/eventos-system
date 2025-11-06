#!/bin/bash

echo "📊 Status dos Microsserviços"
echo "=============================="
echo ""

check_service() {
    local service=$1
    local port=$2
    
    if [ -f logs/${service}.pid ]; then
        local pid=$(cat logs/${service}.pid)
        if ps -p ${pid} > /dev/null 2>&1; then
            # Verificar se a porta está realmente escutando
            if command -v lsof &> /dev/null; then
                if lsof -Pi :${port} -sTCP:LISTEN -t > /dev/null 2>&1; then
                    echo "✅ ${service} (PID: ${pid}) - Porta: ${port} - RODANDO"
                else
                    echo "⚠️  ${service} (PID: ${pid}) - Processo existe mas porta ${port} não está escutando"
                fi
            else
                echo "✅ ${service} (PID: ${pid}) - Porta: ${port} - RODANDO"
            fi
        else
            echo "❌ ${service} - PID inválido (processo não existe)"
            rm logs/${service}.pid
        fi
    else
        echo "⚪ ${service} - NÃO INICIADO"
    fi
}

# Verificar todos os microsserviços
check_service "auth-service" "8001"
check_service "eventos-service" "8002"
check_service "usuarios-service" "8003"
check_service "inscricoes-service" "8004"
check_service "ingressos-service" "8005"
check_service "checkins-service" "8006"
check_service "certificados-service" "8007"

echo ""
echo "💡 Dicas:"
echo "   Ver logs: bash logs.sh [servico]"
echo "   Testar API: curl http://localhost:8001/"
