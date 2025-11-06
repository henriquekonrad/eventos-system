#!/bin/bash

echo "🛑 Parando todos os microsserviços..."
echo ""

stop_service() {
    local service=$1
    
    if [ -f logs/${service}.pid ]; then
        local pid=$(cat logs/${service}.pid)
        if ps -p ${pid} > /dev/null 2>&1; then
            echo "  ⛔ Parando ${service} (PID: ${pid})..."
            kill ${pid} 2>/dev/null
            sleep 1
            # Força se ainda estiver rodando
            if ps -p ${pid} > /dev/null 2>&1; then
                kill -9 ${pid} 2>/dev/null
            fi
        else
            echo "  ⚠️  ${service} já estava parado"
        fi
        rm logs/${service}.pid
    else
        echo "  ⚪ ${service} não estava rodando"
    fi
}

# Parar todos os microsserviços
stop_service "auth-service"
stop_service "eventos-service"
stop_service "usuarios-service"
stop_service "inscricoes-service"
stop_service "ingressos-service"
stop_service "checkins-service"
stop_service "certificados-service"

echo ""
echo "✅ Todos os serviços foram parados!"
