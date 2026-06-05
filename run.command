#!/bin/bash
cd "$(dirname "$0")"
echo "Starting CAIH..."
python3 -m streamlit run src/main.py
