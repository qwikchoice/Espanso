#!/bin/bash
cd "$(dirname "$0")/.."

if ! python3 --version &>/dev/null; then
    echo ""
    echo " ERROR: Python not found."
    echo " Install Python from https://python.org or via: brew install python"
    echo ""
    exit 1
fi

echo " Starting Espanso Manager..."
echo " Your browser will open automatically."
echo " Press Ctrl+C to stop the server."
echo ""
python3 "$(dirname "$0")/../espanso_server.py"
if [ $? -ne 0 ]; then
    echo ""
    echo " Server exited with an error."
    read -p " Press Enter to continue..."
fi
