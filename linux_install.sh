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

echo "[+] Downloading the Gemma 4 Cloud model..."
ollama pull gemma4:31b-cloud

echo "[+] Installing Python libraries..."
pip3 install -r requirements.txt --break-system-packages

echo "[+] Setup complete! Launching CAIH..."
python3 -m streamlit run src/main.py
