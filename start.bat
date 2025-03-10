@echo off
setlocal

:: Activate virtual environment
call "%~dp0.venv\Scripts\activate.bat"

:: Run the Python script
python "%~dp0main.py"

endlocal