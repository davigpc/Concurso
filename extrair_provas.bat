@echo off
title Extrair Novas Provas - PrepConcursos
cd /d "%~dp0"

echo ===================================================
echo     PrepConcursos - Extracao e Preparacao de Provas
echo ===================================================
echo.

python --version >nul 2>&1
if errorlevel 1 goto NO_PYTHON

echo [0/4] Sincronizando novos PDFs na pasta 'provas/'...
echo ---------------------------------------------------
python scripts/gerar_config_prova.py
if errorlevel 1 goto ERR_SYNC

echo.
echo [1/4] Extraindo questoes dos PDFs na pasta 'provas/'...
echo ---------------------------------------------------
python scripts/extract_questions.py
if errorlevel 1 goto ERR_EXTRACT

echo.
echo [2/4] Aplicando gabaritos e atualizando a base de dados...
echo ---------------------------------------------------
python scripts/patch_db.py
if errorlevel 1 goto ERR_PATCH

echo.
echo [3/4] Validando integridade da base de dados gerada...
echo ---------------------------------------------------
python scripts/check_json.py
if errorlevel 1 goto ERR_CHECK

echo.
echo ===================================================
echo   [SUCESSO] Processamento de provas concluido!
echo   Arquivos 'questions.json' e 'questions.js' atualizados.
echo ===================================================
goto END

:NO_PYTHON
echo.
echo [ERRO] Python nao foi encontrado no PATH do sistema.
echo Por favor, instale o Python 3 (https://www.python.org/) e marque "Add Python to PATH".
goto END

:ERR_SYNC
echo.
echo [ERRO] Ocorreu uma falha ao executar scripts/gerar_config_prova.py.
goto END

:ERR_EXTRACT
echo.
echo [ERRO] Ocorreu uma falha ao executar scripts/extract_questions.py.
echo Certifique-se de ter instalado a biblioteca PyMuPDF: pip install pymupdf
goto END

:ERR_PATCH
echo.
echo [ERRO] Ocorreu uma falha ao executar scripts/patch_db.py.
goto END

:ERR_CHECK
echo.
echo [AVISO] Ocorreu um alerta durante a verificacao dos dados.
goto END

:END
echo.
pause
