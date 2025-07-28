#!/bin/bash

echo "=== I2M2G Setup (WSL) ==="
echo ""

# Get the WSL IP address - try multiple methods for WSL compatibility
HOST_IP=""

# Method 1: Try to get IP from eth0 (common in WSL)
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(ip -4 addr show eth0 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)
fi

# Method 2: Try to get IP from default route interface
if [ -z "$HOST_IP" ]; then
    DEFAULT_IFACE=$(ip route 2>/dev/null | awk '/default/ {print $5}' | head -n 1)
    if [ ! -z "$DEFAULT_IFACE" ]; then
        HOST_IP=$(ip -4 addr show "$DEFAULT_IFACE" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)
    fi
fi

# Method 3: Try to get IP from any interface
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
fi

# Method 4: Use hostname -I as fallback
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
fi

# Method 5: Use curl to get external IP (last resort)
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(curl -s --max-time 5 ifconfig.me 2>/dev/null || curl -s --max-time 5 ipinfo.io/ip 2>/dev/null)
fi

# Validate that we got an IP
if [ -z "$HOST_IP" ]; then
    echo "❌ Could not determine IP address. Please check your WSL network connection."
    echo "   Try running: ip addr show"
    echo "   Or manually set your IP in the .env file"
    exit 1
fi

echo "✅ Retrieved Host IP: $HOST_IP"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    if [ -f "env.template" ]; then
        # Copy template and replace placeholder with retrieved host IP
        cp env.template .env
        
        # Use WSL-compatible sed command (without .bak extension)
        sed -i "s/HOST_IP_PLACEHOLDER/$HOST_IP/g" .env
        
        # Generate a secure token for InfluxDB
        echo "🔑 Generating secure InfluxDB admin token..."
        INFLUXDB_TOKEN=$(openssl rand -hex 32)
        sed -i "s/^INFLUXDB_INIT_ADMIN_TOKEN=.*/INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}/" .env
        echo "   ✅ Generated secure token"
        
        echo "✅ .env file created from env.template with Host IP: $HOST_IP"
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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop for Windows."
    echo "   Make sure Docker Desktop is running and WSL integration is enabled."
    exit 1
fi

echo "✅ Docker is running"

docker compose up --build -d

sleep 5
docker compose logs -f meter2mqtt 