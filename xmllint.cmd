@echo off
setlocal
cd /d "%~dp0"
python xmllint.py %*
endlocal
