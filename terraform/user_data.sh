#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Update the instance
sudo yum update -y

# Install Python3 and pip3
sudo yum install -y python3 python3-pip git mesa-libGL

# Configure pip to use a faster mirror
mkdir -p ~/.pip
echo "[global]" > ~/.pip/pip.conf
echo "index-url = https://pypi.tuna.tsinghua.edu.cn/simple" >> ~/.pip/pip.conf

# Verify installation
python3 --version
pip3 --version

# Clone the GitHub repository
git clone https://github.com/vumichien/eisei-ai-terraform.git /app

# Change to the app directory
cd /app/app

# Install application dependencies
pip3 install -r requirements.txt

# Start FastAPI app
nohup uvicorn main:app --host 0.0.0.0 --port 80 &
