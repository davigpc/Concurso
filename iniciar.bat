@echo off
title PrepConcursos - Servidor & Frontend
cd /d "%~dp0"

echo =========================================
echo    Iniciando Servidor SQLite + Vite
echo =========================================
echo.

if not exist "node_modules\" (
    echo [INFO] pasta node_modules nao encontrada. Instalando dependencias...
    call npm install
    echo.
)

if not exist "concurso.db" (
    echo [INFO] Banco de dados SQLite nao encontrado. Inicializando e extraindo...
    call python scripts/cv_extract_questions.py
    echo.
)

echo [1/2] Iniciando API REST SQLite na porta 3001...
start "PrepConcursos - API Backend" /min node server.js

timeout /t 2 /nobreak >nul

echo [2/2] Iniciando o servidor frontend Vite...
call npm run dev -- --open

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Ocorreu um problema ao iniciar a aplicacao.
    pause
)
