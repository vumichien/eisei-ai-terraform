#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Update the instance
sudo yum update -y

# Install Python3 and pip3
sudo yum install -y python3 python3-pip git mesa-libGL
pip3 install virtualenv

# Create a virtual environment
virtualenv /home/ec2-user/venv

# Activate the virtual environment
source /home/ec2-user/venv/bin/activate

# Clone the GitHub repository
git clone https://github.com/vumichien/eisei-ai-terraform.git /app

# Change to the app directory
cd /app/app

# Install application dependencies
pip3 install -r requirements.txt

# Adjust permissions if necessary
sudo chown -R ec2-user:ec2-user /app/app
sudo chown -R ec2-user:ec2-user /home/ec2-user/venv
