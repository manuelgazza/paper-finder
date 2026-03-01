#!/bin/bash
# Paper Hunter - Wrapper script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Python path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run paper hunter
python paper_hunter.py "$@"
