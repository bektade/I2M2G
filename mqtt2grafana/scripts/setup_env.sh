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

# # Prompt for Meter IP
# echo ""
# echo "🔌 METER CONFIGURATION (VERY IMPORTANT)"
# echo "----------------------"
# prompt_secure "METER_IP" "10.28.10.xx" "Meter IP address"
# prompt_secure "METER_PORT" "8081" "Meter communication port"



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