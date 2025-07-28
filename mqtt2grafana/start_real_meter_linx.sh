#!/bin/bash

# I2M2G - Start Real Meter Script
# This script automates the setup and startup process for real meter monitoring

set -e  # Exit on any error

echo "=== I2M2G Real Meter Setup ==="
echo "Starting automated setup process..."
echo ""

# Step 1: Check if SSL keys exist

echo "Step 1: Checking for existing SSL keys..."
KEY_OUTPUT=$(./scripts/generate_keys.sh -p)

if [[ -n "$KEY_OUTPUT" ]]; then
    echo "✅ SSL keys found."
    echo "$KEY_OUTPUT"
else
    echo "❌ SSL keys not found. Generating new keys..."
    ./scripts/generate_keys.sh
    echo "✅ New SSL keys generated."
    echo "Displaying generated keys..."
    ./scripts/generate_keys.sh -p
fi



# Step 3: Create .env file
echo ""
echo "Step 4: Creating .env file..."
./scripts/setup_env.sh

# Update .env file with detected IP
echo "Updating .env file with detected host IP..."
sed -i.bak "s/^SIMULATOR_IP=.*/SIMULATOR_IP=${HOST_IP}/" .env
rm -f .env.bak
echo "✅ Updated SIMULATOR_IP in .env file: $HOST_IP"

# Step 5: Start services in background
echo ""
echo ""
echo "Step 5: Starting Docker services in background..."
docker compose --profile real_meter up --build -d

# Wait a moment for services to start
echo "Waiting for services to start..."
sleep 5

# Step 6: Show logs
echo ""
echo ""
echo "Step 6: Showing logs from xcel_itron2mqtt_I2M2G..."
echo "Press Ctrl+C to stop viewing logs (services will continue running in background)"
echo "=========================================="
docker logs -f xcel_itron2mqtt_I2M2G 