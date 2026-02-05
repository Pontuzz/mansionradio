#!/bin/bash
# Quick setup script for mansion-radio-bot

set -e

echo "[*] MansionNET Radio Bot Setup"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "[*] Found Python $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[*] Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "[*] Creating .env file from template..."
    cp config/.env.example .env
    echo "[!] Edit .env with your configuration before running the bot"
else
    echo "[*] .env file already exists"
fi

echo ""
echo "[✓] Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your IRC server settings"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python src/main.py"
