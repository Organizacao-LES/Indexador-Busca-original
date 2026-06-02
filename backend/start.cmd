@echo off
echo.
echo ==========================
echo IFESDOC - START SERVER
echo %computername% / %username%
echo ==========================
echo.

:: Verifica se a venv existe
if not exist .venv (
    echo [ERRO] .venv nao encontrada. Rode o setup.cmd primeiro.
    pause
    exit /b 1
)

:loop
cls
echo ==========================
echo Reiniciando servidor...
echo ==========================
echo.

:: Ativa o ambiente virtual
call .venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao ativar a venv
    pause
    exit /b 1
)

:: Instala dependencias
pip install -r requirements.txt --quiet

:: Inicia o servidor (AGORA usando a venv corretamente)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

goto loop