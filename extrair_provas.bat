@echo off
title Extrair Provas - PrepConcursos (SQLite + CV)
cd /d "%~dp0"

echo ===================================================
echo   PrepConcursos - Extracao por Visao Computacional
echo ===================================================
echo.

python --version >nul 2>&1
if errorlevel 1 goto NO_PYTHON

echo [1/3] Sincronizando novas provas e gabaritos...
python scripts/gerar_config_prova.py
python scripts/parse_gabarito.py

echo.
echo [2/3] Extraindo questoes via Visao Computacional para concurso.db...
python scripts/cv_extract_questions.py
if errorlevel 1 goto ERR_EXTRACT

echo.
echo ===================================================
echo   [SUCESSO] Processamento de provas concluido!
echo   Banco 'concurso.db' atualizado com sucesso.
echo ===================================================
goto END

:NO_PYTHON
echo [ERRO] Python nao foi encontrado no PATH.
goto END

:ERR_EXTRACT
echo [ERRO] Falha ao executar scripts/cv_extract_questions.py.
goto END

:END
echo.
pause
