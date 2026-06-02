@echo off
echo.
echo ==========================
echo IFESDOC - SETUP DEV LOCAL
echo %computername% / %username%
echo ==========================
echo.

:: ── Verifica Python 3.11 ou 3.12 ─────────────────────────────────────────────
:: Tenta py launcher primeiro (recomendado no Windows)
where py >nul 2>&1
if %errorlevel% == 0 (
    echo Usando py launcher...
    py -3.12 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON=py -3.12
        goto :criar_venv
    )
    py -3.11 --version >nul 2>&1
    if %errorlevel% == 0 (
        set PYTHON=py -3.11
        goto :criar_venv
    )
)

:: Fallback para python direto
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON=python
    goto :criar_venv
)

echo [ERRO] Python nao encontrado. Instale Python 3.11 ou 3.12 em https://python.org
pause
exit /b 1

:criar_venv
echo Python encontrado: %PYTHON%
echo.

:: ── Cria o venv se nao existir ────────────────────────────────────────────────
if exist .venv (
    echo [OK] .venv ja existe, pulando criacao...
) else (
    echo Criando ambiente virtual .venv ...
    %PYTHON% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar venv
        pause
        exit /b 1
    )
    echo [OK] .venv criado
)

echo.

:: ── Ativa e instala dependencias ──────────────────────────────────────────────
echo Ativando venv e instalando dependencias...
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha na instalacao das dependencias
    pause
    exit /b 1
)

echo.
echo ==========================
echo [OK] Setup concluido!
echo ==========================
echo.
echo Para ativar o venv manualmente:
echo   .venv\Scripts\activate
echo.
echo Para rodar a API:
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
pause