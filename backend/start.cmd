@echo off
echo.
echo ==========================
echo IFESDOC - START SERVER
echo %computername% / %username%
echo ==========================
echo.

:: Garante que usa Python 3.12 (tem wheel do psycopg2-binary)
set PYTHON=py -3.12

:: Verifica se 3.12 esta disponivel
%PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python 3.12 nao encontrado.
    echo Instale em: https://python.org/downloads/release/python-3127
    pause
    exit /b 1
)

:loop
cls
echo ==========================
echo Reiniciando servidor...
echo ==========================
echo.

%PYTHON% -m pip install -r requirements.txt --quiet
%PYTHON% -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo Servidor encerrado. Reiniciando em 20s... (Ctrl+C para parar)
timeout 20

goto loop