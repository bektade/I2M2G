#!/bin/bash

echo "=== I2M2G Setup ==="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# I2M2G Environment Configuration

# Simulator Configuration
SIMULATOR_IP=10.195.251.91
SIMULATOR_PORT=8082

# MQTT Configuration
MQTT_SERVER=mqtt
MQTT_PORT=1883
MQTT_TOPIC_PREFIX=xcel_itron_5/

# Database Configuration
INFLUXDB_INIT_USERNAME=admin
INFLUXDB_INIT_PASSWORD=adminpassword
INFLUXDB_INIT_ORG=myorg
INFLUXDB_INIT_BUCKET=power_usage
INFLUXDB_INIT_ADMIN_TOKEN=super-secret-key

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# Logging
LOGLEVEL=INFO
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "=== Starting I2M2G ==="
echo "This will start the complete monitoring stack."
echo ""

docker-compose up --build 