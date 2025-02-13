#!/usr/bin/env bash

VENV_DIR=".venv"

echo "🚀 Criando e ativando o ambiente virtual..."

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
    echo "✅ Ambiente virtual criado!"
else
    echo "⚡ Ambiente virtual já existe."
fi

echo "🔹 Ativando o ambiente virtual..."
source $VENV_DIR/bin/activate

echo "📦 Atualizando pip..."
pip install --upgrade pip
pip install mysql
pip install mysqlclient

if [ -f "requirements.txt" ]; then
    echo "📂 Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Arquivo requirements.txt não encontrado!"
fi

echo "✅ Setup concluído! O ambiente virtual está ativado automaticamente."

exec bash
