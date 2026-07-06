@echo off
echo Instalando dependencias...
pip install -r requirements.txt
echo.
echo Iniciando servidor MCP local na porta 8000...
python server.py
pause
