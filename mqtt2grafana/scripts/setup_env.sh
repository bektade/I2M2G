#!/bin/bash

# =============================================================================
# XCEL ITRON2MQTT - ENVIRONMENT SETUP SCRIPT
# =============================================================================
# This script helps you set up your .env file securely
# =============================================================================

set -e

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Your existing .env file is preserved."
        exit 1
    fi
fi

# Copy template to .env
if [ -f "env.template" ]; then
    cp env.template .env
    echo "✅ Created .env file from template"
else
    echo "❌ Error: env.template not found!"
    exit 1
fi

echo ""
echo "🔧 ENVIRONMENT VARIABLES SETUP"
echo "==============================="


# Function to prompt for secure input
prompt_secure() {
    local var_name=$1
    local default_value=$2
    local description=$3
    
    echo "📝 $description"
    if [ -n "$default_value" ]; then
        echo "   Default: $default_value"
        read -p "   Enter new value (or press Enter to keep default): " value
        if [ -z "$value" ]; then
            value="$default_value"
        fi
    else
        read -s -p "   Enter value: " value
        echo
    fi
    
    # Update .env file
    sed -i.bak "s/^${var_name}=.*/${var_name}=${value}/" .env
    rm -f .env.bak
}


# Detect host IP address for Linux
#!/bin/bash

# Detect host IP address for Linux
DEFAULT_IFACE=$(ip route | awk '/default/ {print $5}' | head -n 1)
HOST_IP=$(ip -4 addr show "$DEFAULT_IFACE" | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)

# Validate that we got an IP
if [ -z "$HOST_IP" ]; then
    echo "❌ Could not determine IP address. Please check your network connection."
    exit 1
fi

# Update SIMULATOR_IP in .env file
if [ -f .env ]; then
    if grep -q "^SIMULATOR_IP=" .env; then
        sed -i.bak "s/^SIMULATOR_IP=.*/SIMULATOR_IP=$HOST_IP/" .env
    else
        echo "SIMULATOR_IP=$HOST_IP" >> .env
    fi
    rm -f .env.bak
else
    echo "SIMULATOR_IP=$HOST_IP" > .env
fi
echo "✅ SIMULATOR_IP updated in .env file: $HOST_IP"





# Generate a secure token for InfluxDB
echo "🔑 Generating secure InfluxDB admin token..."
INFLUXDB_TOKEN=$(openssl rand -hex 32)
sed -i.bak "s/^INFLUXDB_INIT_ADMIN_TOKEN=.*/INFLUXDB_INIT_ADMIN_TOKEN=${INFLUXDB_TOKEN}/" .env
rm -f .env.bak
echo "   ✅ Generated secure token: ${INFLUXDB_TOKEN}"




# echo ""
# echo "LOGGING CONFIGURATION"
# echo "----------------------------"

# prompt_secure "LOGLEVEL" "DEBUG" "Logging level (DEBUG, INFO, WARNING, ERROR)"

echo ""
echo "✅ .env SETUP COMPLETE!"
echo "CUSOMIZE YOUR SETTINGS AS NEEDED in .env file"
echo "=============================="