#!/usr/bin/env python3

import subprocess
import sys
import os
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Run CardAssist Streamlit Chatbot")
parser.add_argument(
    "--log-level",
    type=str,
    default="INFO",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    help="Set the logging level (default: INFO)"
)
args = parser.parse_args()

# Activate the venv
venv_python = ".././venv_cardassist_10/bin/python"
app_script = "main.py"

# Ensure the virtual environment exists
if not os.path.exists(venv_python):
    print(f"Error: Virtual environment Python executable not found at {venv_python}")
    sys.exit(1)

# Run Streamlit explicitly from the venv, passing --log-level
command = [
    venv_python, "-m", "streamlit", "run", app_script, "--", "--log-level", args.log_level
]
try:
    subprocess.run(command, check=True)
except subprocess.CalledProcessError as e:
    print(f"Error running Streamlit: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nStopped by user")
    sys.exit(0)