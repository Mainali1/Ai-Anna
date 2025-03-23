@echo off
echo Setting up Anna AI Assistant to start automatically on Windows startup...

:: Get the current directory
set CURRENT_DIR=%~dp0

:: Create a shortcut in the Windows Startup folder
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut([Environment]::GetFolderPath('Startup') + '\Anna AI Assistant.lnk'); $Shortcut.TargetPath = '%CURRENT_DIR%start.bat'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = 'Anna AI Assistant'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo Anna AI Assistant has been successfully set up to start automatically on Windows startup.
) else (
    echo Failed to set up automatic startup. Please try running this script as administrator.
)

pause