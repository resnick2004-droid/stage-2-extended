#!/bin/sh
# Rebuild "EV Backtest Results.zip" next to this repository folder. Run after every change.
cd "$(dirname "$0")/.." && rm -f "EV Backtest Results.zip" && \
zip -qr "EV Backtest Results.zip" propsim -x "*/__pycache__/*" "*/.pytest_cache/*" "*/log_*.txt" && \
echo "zip rebuilt: $(unzip -Z1 'EV Backtest Results.zip' | grep -v '/$' | wc -l) files"
