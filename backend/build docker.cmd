@echo off
docker build -t backend-api-python .
docker ps
timeout 10