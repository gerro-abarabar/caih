#!/bin/bash

echo "Checking for Homebrew (Mac package manager)..."
if ! command -v brew &> /dev/null; then
    echo "[+] Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

echo "Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo "[+] Installing Python 3.12..."
    brew install python@3.12
else
    echo "[✓] Python is already installed."
fi

echo "Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "[+] Installing Ollama..."
    brew install --cask ollama
    echo "[+] Starting Ollama service..."
    open -a Ollama
    sleep 5
else
    echo "[✓] Ollama is already installed."
fi

echo "[+] Checking Ollama Cloud authentication..."
if ! ollama list &> /dev/null; then
    echo "[!] An Ollama account is required to use cloud models."
    echo "[!] Opening your browser... please sign in or create a free account."
    read -p "Press [Enter] to open the login page..."
    ollama signin
fi

echo "[+] Downloading the Gemma 4 Cloud model..."
ollama pull gemma4:31b-cloud

echo "[+] Installing Python libraries..."
pip3 install -r requirements.txt

echo "[+] Setup complete! Launching CAIH..."
python3 -m streamlit run src/main.py
