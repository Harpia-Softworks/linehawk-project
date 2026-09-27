#!/bin/bash
echo ">>> Entering Virtual Environment (venv)..."
source .venv/bin/activate
    # Run the game.
    PYTHONPATH=./source python3 -m linehawk.cmds.game
deactivate
echo ">>> Left Virtual Environment (venv)!"