@echo off
:loop
cls
echo Restarting Server...
py main.py
timeout 10

goto loop