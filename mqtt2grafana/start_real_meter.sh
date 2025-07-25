#!/bin/bash

# I2M2G - Start Real Meter Script
# This script automates the setup and startup process for real meter monitoring

set -e  # Exit on any error

echo "=== I2M2G Real Meter Setup ==="
echo "Starting automated setup process..."
echo ""

# Step 1: Check if SSL keys exist
echo "Step 1: Checking for existing SSL keys..."
if ./scripts/generate_keys.sh -p; then
    echo "✅ SSL keys found."
else
    echo "❌ SSL keys not found. Generating new keys..."
    ./scripts/generate_keys.sh
    echo "✅ New SSL keys generated."
    echo "Displaying generated keys..."
    ./scripts/generate_keys.sh -p
fi

echo ""
echo "Step 2: Detecting host IP address... (not needed for real meter)"

# Ask user if they are on a Mac
read -p "Are you running this script on a Mac? (y/n): " is_mac

if [[ "$is_mac" == "y" || "$is_mac" == "Y" ]]; then
    HOST_IP=$(ipconfig getifaddr en0)
else
    # Try to get the IP address from the default route interface on Linux
    DEFAULT_IFACE=$(ip route | awk '/default/ {print $5}' | head -n 1)
    HOST_IP=$(ip -4 addr show "$DEFAULT_IFACE" | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)
fi

# Validate that we got an IP
if [ -z "$HOST_IP" ]; then
    echo "Could not determine IP address. Please check your network connection."
    exit 1
fi
echo "Retrieved Host IP: $HOST_IP"


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