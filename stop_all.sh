#!/bin/bash

echo "🛑 Parando todos os microsserviços..."
echo ""

stop_node_service() {
    local service=$1
    local pid_file="${LOG_DIR}/${service}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "  ⛔ Parando ${service} (PID: ${pid})..."
            kill $pid 2>/dev/null
            sleep 1
            if ps -p $pid > /dev/null 2>&1; then
                echo "  ⚠️  ${service} ainda está rodando — forçando parada"
                kill -9 $pid 2>/dev/null
            fi
        else
            echo "  ⚠️  ${service} - PID encontrado mas processo inexistente"
        fi
        pkill -f "node src/server.js" 2>/dev/null
        rm -f "$pid_file"
    else
        # tenta encontrar via processo caso não tenha pid file
        local found_pid=$(ps aux | grep "npm start" | grep "${service}" | grep -v grep | awk '{print $2}')
        if [ ! -z "$found_pid" ]; then
            echo "  ⛔ Parando ${service} (detectado PID: ${found_pid})..."
            kill $found_pid 2>/dev/null
            sleep 1
            if ps -p $found_pid > /dev/null 2>&1; then
                kill -9 $found_pid 2>/dev/null
            fi
        else
            echo "  ⚪ ${service} não estava rodando"
        fi
    fi
}

stop_service() {
    local service=$1
    local pid_file="logs/${service}.pid"

    # Se existir PID, tenta parar normalmente
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "  ⛔ Parando ${service} (PID: ${pid})..."
            kill $pid 2>/dev/null
            sleep 1
            if ps -p $pid > /dev/null 2>&1; then
                echo "  ⚠️  ${service} ainda está rodando — forçando parada"
                kill -9 $pid 2>/dev/null
            fi
        else
            echo "  ⚠️  ${service} - PID encontrado mas processo inexistente"
        fi
        rm -f "$pid_file"
    else
        # Tenta encontrar manualmente se rodando via nome
        local found_pid=$(ps aux | grep "uvicorn.*${service}" | grep -v grep | awk '{print $2}')
        if [ ! -z "$found_pid" ]; then
            echo "  ⛔ Parando ${service} (detectado PID: ${found_pid})..."
            kill $found_pid 2>/dev/null
            sleep 1
            if ps -p $found_pid > /dev/null 2>&1; then
                kill -9 $found_pid 2>/dev/null
            fi
        else
            echo "  ⚪ ${service} não estava rodando"
        fi
    fi
}

# Lista de serviços
SERVICES=(
    "auth-service"
    "eventos-service"
    "usuarios-service"
    "inscricoes-service"
    "ingressos-service"
    "checkins-service"
    "certificados-service"
)

for service in "${SERVICES[@]}"; do
    stop_service "$service"
done

stop_node_service "email-service"

echo ""
echo "✅ Todos os serviços foram parados!"
