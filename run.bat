@echo off
REM Sobe a aplicacao de alinhamento de duas sequencias em um unico comando:
REM cria/usa um venv, instala as dependencias e inicia o servidor na porta 8000.
setlocal

cd /d "%~dp0"

if not exist ".venv" (
    echo Criando ambiente virtual ^(.venv^)...
    python -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Instalando dependencias...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

echo.
echo Aplicacao disponivel em: http://localhost:8000
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000

endlocal
