@echo off
:loop
echo restarting server...
npm run start
timeout 10
goto loop
pause