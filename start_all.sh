#!/bin/bash
# ==========================================
# 🚀 Script para iniciar todos os microsserviços
# ==========================================

source ~/eventos/venv/bin/activate

LOG_DIR=~/eventos/logs
APP_DIR=~/eventos/eventos-api

mkdir -p "$LOG_DIR"

start_service() {
    local service_name=$1
    local port=$2
    local module_name="app.services.${service_name}.main:app"
    local log_file="${LOG_DIR}/${service_name}.log"
    local pid_file="${LOG_DIR}/${service_name}.pid"

    echo "🚀 Iniciando ${service_name} na porta ${port}..."

    # Evita instâncias duplicadas
    if [ -f "$pid_file" ] && ps -p $(cat "$pid_file") > /dev/null 2>&1; then
        echo "⚠️  ${service_name} já está em execução (PID $(cat $pid_file))"
        return
    fi

    cd "$APP_DIR"
    nohup uvicorn "$module_name" --host 0.0.0.0 --port "$port" > "$log_file" 2>&1 &
    echo $! > "$pid_file"

    sleep 1
    if ps -p $(cat "$pid_file") > /dev/null 2>&1; then
        echo "✅ ${service_name} iniciado (PID $(cat $pid_file))"
    else
        echo "❌ Falha ao iniciar ${service_name}. Veja o log em ${log_file}"
    fi
}

echo "=========================================="
echo "🚀 Iniciando todos os microsserviços..."
echo "=========================================="

start_service "auth-service" 8001
start_service "eventos-service" 8002
start_service "usuarios-service" 8003
start_service "inscricoes-service" 8004
start_service "ingressos-service" 8005
start_service "checkins-service" 8006
start_service "certificados-service" 8007

echo ""
echo "📊 Use './status.sh' para verificar o status dos serviços."
