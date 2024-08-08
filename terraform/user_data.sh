#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Activate the virtual environment
source /home/ec2-user/venv/bin/activate

# Change to the app directory
cd /app/app

# Start FastAPI app on port 8080
nohup uvicorn main:app --host 0.0.0.0 --port 8080 &
