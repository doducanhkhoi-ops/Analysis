@echo off
setlocal
cd /d "%~dp0"
python strategic_report_flow.py %*
endlocal
