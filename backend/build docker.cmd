@echo off
echo.
echo ==========================
echo LDA BUILDER DOCKER
echo %computername%
echo %username%
echo %cd%
echo DATABASE_URL=postgres://%DATABASE_USER%:%DATABASE_PASSWORD%@%DATABASE_HOST%:%DATABASE_PORT%/ifesdoc
echo ==========================
echo.

docker build -f Dockerfile.windows -t backend .
docker run -d -p 8000:8000 ^
--name backend_%computername% ^
-e DATABASE_URL=postgres://%DATABASE_USER%:%DATABASE_PASSWORD%@%DATABASE_HOST%:%DATABASE_PORT%/ifesdoc ^
backend
docker ps
timeout 10