#!/bin/bash

echo "[+] Updating package lists..."
sudo apt update -y && sudo apt upgrade -y

echo "[+] Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "[+] Installing Python 3 and pip..."
    sudo apt install python3 python3-pip -y
else
    echo "[✓] Python is already installed."
fi

echo "[+] Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "[+] Installing Ollama via official installer..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "[+] Starting Ollama service..."
    sudo systemctl start ollama
    sleep 5
else
    echo "[✓] Ollama is already installed."
fi

echo "[+] Verifying Cloud Account Status..."
if ! python3 check_auth.py; then
    echo ""
    echo "[!] ALERT: An Ollama account is REQUIRED to execute Cloud Models."
    echo "[!] Opening your default browser... please sign in or register."
    echo ""
    read -p "Press [Enter] to launch the browser connection portal..."
    ollama signin
    sleep 3
fi

echo "[+] Downloading the Gemma 4 Cloud model..."
ollama pull gemma4:31b-cloud

echo "[+] Installing Python libraries..."
pip3 install -r requirements.txt --break-system-packages

echo "[+] Setup complete! Launching CAIH..."
python3 -m streamlit run src/main.py
