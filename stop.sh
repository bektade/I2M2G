#!/bin/bash

# Clean up after running Meter Simulator 
# This script cleans up Docker containers, networks, and system resources

set -e  # Exit on any error

echo "=== Meter Simulator ==="
echo "Starting cleanup process..."

# Step 1: Stop and remove containers
echo "Step 1: Stopping and removing containers..."
docker compose down -vv

# Step 2: Remove Docker volumes (including InfluxDB data)
echo "Step 2: Removing Docker volumes..."
docker volume prune -f

# Step 3: Remove unused networks
echo "Step 3: Removing unused networks..."
docker network prune -f

# Step 4: Clean up Docker system
echo "Step 4: Cleaning up Docker system..."
docker system prune -f

# Step 5: Remove .env file if it exists
if [ -f ".env" ]; then
    echo "Step 5: Removing .env file..."
    rm -f .env
else
    echo "No .env file found, skipping removal."
fi

echo "=== Cleanup Complete ==="
echo "All containers, networks, volumes, and unused Docker resources have been removed." 