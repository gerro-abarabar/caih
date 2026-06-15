@echo off
:: Ensure admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Please right-click this file and select "Run as Administrator"
    pause
    exit /b
)

echo [+] Checking for a REAL Python installation...
:: Check if python runs and returns a valid version string
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Real Python not found (or caught the Microsoft Store alias)
    echo [+] Installing Python 3.12 via WinGet...
    winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements

    :: Force the script to see the new Python path immediately without restarting cmd
    refreshenv >nul 2>nul || set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\"
) else (
    echo [✓] Real Python is already installed.
)

echo [+] Checking and Installing Ollama...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    winget install Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
    echo [+] Launching Ollama background service...
    startd "" "ollama serve"
    timeout /t 5 >nul
) else (
    echo [✓] Ollama is already installed.
)

:: Force the script to run from its own folder directory
cd /d "%~dp0"

: checking
echo [+] Verifying Cloud Account Status...
python src/check_ollama.py
if %errorlevel% neq 0 (
    echo.
    echo [!] ALERT: An Ollama account is REQUIRED to execute Cloud Models.
    echo [!] Opening your default browser... please sign in or register.
    echo.
    pause
    ollama signin
    goto checking

)
echo [+] Account synced! Proceeding...

echo [+] Downloading the Gemma 4 Cloud model...
ollama pull gemma4:31b-cloud



echo [+] Installing Python libraries...
:: Using 'python -m pip' ensures we use the exact Python we just checked/installed
python -m pip install -r requirements.txt

echo [+] Setup complete! Launching CAIH...
python -m streamlit run src/main.py
pause
