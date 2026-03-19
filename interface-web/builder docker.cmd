@echo off
echo.
echo ==========================
echo LDA BUILDER DOCKER
echo %computername%
echo %username%
echo %cd%
echo ==========================
echo.

docker build -t frontend .
docker run -d -p 8080:8080 --name frontend_%computername% frontend
docker ps
timeout 10