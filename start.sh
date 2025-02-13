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

if [ -f "requirements.txt" ]; then
    echo "📂 Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Arquivo requirements.txt não encontrado!"
fi

echo "✅ Setup concluído! O ambiente virtual está ativado automaticamente."

export QT_QPA_PLATFORM_PLUGIN_PATH=$(python3 -c "import PySide6.QtCore; print(PySide6.QtCore.QLibraryInfo.path(PySide6.QtCore.QLibraryInfo.PluginsPath))")

exec bash
