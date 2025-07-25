#!/bin/bash

# I2M2G - Start Real Meter Script
# This script automates the setup and startup process for real meter monitoring

set -e  # Exit on any error

echo "=== I2M2G Simulator to MQTT Setup ==="
echo "Starting automated setup process..."

# Step 3: Create .env file
echo "Step 1: Creating .env file..."
./scripts/setup_env.sh

# Step 4: Start services in background
echo "Step 2: Starting MQTT ..."
docker compose up --build -d

# Wait a moment for services to start
echo "Now run main_publishData.py ..."


