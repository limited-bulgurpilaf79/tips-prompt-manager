@echo off
set "APP_DIR=%~dp0"
where pythonw.exe >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw.exe "%APP_DIR%PromptManager.pyw"
) else (
    start "" pyw "%APP_DIR%PromptManager.pyw"
)
