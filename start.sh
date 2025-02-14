#!/usr/bin/env bash

VENV_DIR=".venv"

echo "Criando e ativando o ambiente virtual..."

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
    echo "Ambiente virtual criado!"
else
    echo "Ambiente virtual já existe."
fi

echo "Ativando o ambiente virtual..."
source $VENV_DIR/bin/activate

echo "Atualizando pip..."
pip install --upgrade pip --break-system-packages

if [ -f "requirements.txt" ]; then
    echo "Instalando dependências do requirements.txt..."
    
    pip install --break-system-packages -r requirements.txt

    REQUIRED_PACKAGES=("mysql-connector-python" "PySide6" "pandas" "numpy" "requests")

    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! python3 -c "import ${package//-/_}" &> /dev/null; then
            echo "⚠️ Pacote $package não foi encontrado. Instalando manualmente..."
            pip install --break-system-packages "$package"
        else
            echo "Pacote $package instalado corretamente."
        fi
    done

else
    echo "⚠️ Arquivo requirements.txt não encontrado!"
fi

echo "Setup concluído! O ambiente virtual está ativado automaticamente."

exec bash
