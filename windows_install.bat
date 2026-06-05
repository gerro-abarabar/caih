@echo off
:: Ensure admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Please right-click this file and select "Run as Administrator".
    pause
    exit /b
)

echo [+] Checking and Installing Python via WinGet...
where python >nul 2>nul
if %errorlevel% neq 0 (
    winget install Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
    :: Refresh path variables immediately without requiring a restart
    refreshenv >nul 2>nul || set "PATH=%PATH%;C:\Program Files\Python312\;C:\Program Files\Python312\Scripts\"
) else (
    echo [✓] Python is already installed.
)

echo [+] Checking and Installing Ollama...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    winget install Ollama.Ollama --silent --accept-source-agreements --accept-package-agreements
    echo [+] Launching Ollama background service...
    start "" "ollama serve"
    timeout /t 5 >nul
) else (
    echo [✓] Ollama is already installed.
)

echo [+] Downloading the Gemma 4 Cloud model...
ollama pull gemma4:31b-cloud

echo [+] Installing Python libraries...
pip install -r requirements.txt

echo [+] Setup complete! Launching CAIH...
streamlit run src/main.py
pause
