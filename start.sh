#!/bin/sh

# Start the dashboard server in the background (Hugging Face routes port 7860)
python dashboard.py &

# Start the automation loop
python terabox_automator.py
