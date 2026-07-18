@echo off
title Iniciar Aplicacao - Concurso
cd /d "%~dp0"

echo =========================================
echo    Iniciando Servidor de Desenvolvimento
echo =========================================
echo.

if not exist "node_modules\" (
    echo [INFO] pasta node_modules nao encontrada. Instalando dependencias...
    call npm install
    echo.
)

echo Iniciando o servidor Vite...
call npm run dev -- --open

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu um problema ao iniciar a aplicacao.
    pause
)
