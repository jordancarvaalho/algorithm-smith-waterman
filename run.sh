#!/bin/sh
# Sobe a aplicação de alinhamento de duas sequências em um único comando:
# cria/usa um venv, instala as dependências e inicia o servidor na porta 8000.
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual (.venv)..."
    python3 -m venv .venv
fi

. .venv/bin/activate

echo "Instalando dependências..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo ""
echo "Aplicação disponível em: http://localhost:8000"
echo ""
uvicorn app.main:app --host 0.0.0.0 --port 8000
