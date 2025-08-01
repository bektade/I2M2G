#!/bin/bash

# I2M2G - Remove Real Meter Script
# This script cleans up Docker containers, networks, and system resources

set -e  # Exit on any error

echo "=== I2M2G Real Meter Cleanup ==="
echo "Starting cleanup process..."

# Step 1: Stop and remove containers
echo "Step 1: Stopping and removing containers..."
docker compose down -vv

docker kill meter_001
docker kill meter_002


# Step 2: Remove unused networks
echo "Step 2: Removing unused networks..."
docker network prune -f

# Step 3: Clean up Docker system
echo "Step 3: Cleaning up Docker system..."
docker system prune -f

# Step 4: Remove .env file if it exists
if [ -f ".env" ]; then
    echo "Step 4: Removing .env file..."
    rm -f .env
else
    echo "No .env file found, skipping removal."
fi


echo "=== Cleanup Complete ==="
echo "All containers, networks, and unused Docker resources have been removed." 