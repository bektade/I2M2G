#!/bin/bash

echo "=== I2M2G Setup ==="
echo ""

# Get the simulator IP from en0 interface
SIMULATOR_IP=$(ipconfig getifaddr en0)

# Validate that we got an IP
if [ -z "$SIMULATOR_IP" ]; then
    echo "❌ Could not get IP address from en0 interface. Please check your network connection."
    exit 1
fi

echo "Detected Simulator IP from en0: $SIMULATOR_IP"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f "env.template" ]; then
        # Copy template and replace placeholder with user-provided simulator IP
        cp env.template .env
        sed -i.bak "s/HOST_IP_PLACEHOLDER/$SIMULATOR_IP/g" .env
        rm -f .env.bak 2>/dev/null || true
        
        # Generate a secure token for InfluxDB
        echo "🔑 Generating secure InfluxDB admin token..."
        INFLUXDB_TOKEN=$(openssl rand -hex 32)
        sed -i.bak "s/^INFLUXDB_INIT_ADMIN_TOKEN=.*/INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}/" .env
        rm -f .env.bak 2>/dev/null || true
        echo "   ✅ Generated secure token"
        
        echo "✅ .env file created from env.template with Simulator IP: $SIMULATOR_IP"
    else
        echo "❌ env.template file not found. Please create env.template with your configuration."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "=== Starting I2M2G ==="
echo "This will start the complete monitoring stack."
echo ""

docker-compose up --build -d

sleep 5
docker-compose logs -f meter2mqtt