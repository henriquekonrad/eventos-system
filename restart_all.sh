#!/bin/bash

echo "🔄 Reiniciando todos os microsserviços..."
echo ""

# Parar todos
bash stop_all.sh

echo ""
echo "⏳ Aguardando 3 segundos..."
sleep 3

# Iniciar todos
bash start_all.sh
