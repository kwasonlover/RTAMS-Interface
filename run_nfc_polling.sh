#!/bin/bash

# Navigate to the directory containing the Python script
cd /home/rpi4/Desktop/py532

# Activate the virtual environment
source /home/rpi4/Desktop/py532/.venv/bin/activate

# Run your Python script
echo$(/home/rpi4/Desktop/py532/.venv/bin/python3 /home/rpi4/Desktop/py532/nfc-poll.py) > /home/rpi4/nfc_poll.log 2>&1

