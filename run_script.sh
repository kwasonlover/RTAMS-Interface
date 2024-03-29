#!/bin/bash

# Navigate to the directory containing the Python script
cd /home/rpi4/Desktop/py532

# Activate the virtual environment
source /home/rpi4/Desktop/py532/.venv/bin/activate

# Run your Python script
/home/rpi4/Desktop/py532/.venv/bin/python3 /home/rpi4/Desktop/py532/run.py > /home/rpi4/nfc.log 2>&1

