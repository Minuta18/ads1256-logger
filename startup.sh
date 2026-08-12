#!/bin/bash
set -euo pipefail

echo "Creating virtual environment..."
python3 -m venv ./.venv
source ./.venv/activate
cd seismo

echo "Installing dependencies..."
pip install -r ./requirements.txt

echo "Starting main.py..."
python3 main.py
