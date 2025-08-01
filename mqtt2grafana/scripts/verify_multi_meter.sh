#!/bin/bash

# Multi-Meter Verification Script
# This script helps verify that the multi-meter setup is working correctly

set -e

echo "=========================================="
echo "Multi-Meter Setup Verification Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠${NC} $message"
    else
        echo -e "${RED}✗${NC} $message"
    fi
}

# Check if Docker is running
echo "1. Checking Docker status..."
if docker info >/dev/null 2>&1; then
    print_status "OK" "Docker is running"
else
    print_status "ERROR" "Docker is not running"
    exit 1
fi

# Check if containers are running
echo ""
echo "2. Checking container status..."

containers=("mosquitto" "xcel_itron2mqtt_meter_001_I2M2G" "xcel_itron2mqtt_meter_002_I2M2G" "telegraf" "influxdb" "grafana")

for container in "${containers[@]}"; do
    if docker ps --format "table {{.Names}}" | grep -q "$container"; then
        print_status "OK" "Container $container is running"
    else
        print_status "ERROR" "Container $container is not running"
    fi
done

# Check MQTT topics
echo ""
echo "3. Checking MQTT topics..."

# Function to check MQTT topic
check_mqtt_topic() {
    local topic=$1
    local description=$2
    
    # Use timeout to prevent hanging
    if timeout 10 mosquitto_sub -h localhost -t "$topic" -C 1 -W 5 >/dev/null 2>&1; then
        print_status "OK" "MQTT topic $description is accessible"
    else
        print_status "WARNING" "MQTT topic $description may not be receiving data"
    fi
}

# Check meter-specific topics
check_mqtt_topic "xcel_itron5_meter_001/+/state" "Meter 1 data"
check_mqtt_topic "xcel_itron5_meter_002/+/state" "Meter 2 data"

# Check container logs for errors
echo ""
echo "4. Checking container logs for errors..."

# Function to check container logs
check_container_logs() {
    local container=$1
    local description=$2
    
    if docker logs "$container" --tail 20 2>/dev/null | grep -i "error\|exception\|failed" >/dev/null; then
        print_status "WARNING" "Container $description has errors in logs"
    else
        print_status "OK" "Container $description logs look clean"
    fi
}

check_container_logs "xcel_itron2mqtt_meter_001_I2M2G" "Meter 1"
check_container_logs "xcel_itron2mqtt_meter_002_I2M2G" "Meter 2"
check_container_logs "telegraf" "Telegraf"

# Check InfluxDB data
echo ""
echo "5. Checking InfluxDB data..."

# Function to check InfluxDB data
check_influxdb_data() {
    local measurement=$1
    local meter_id=$2
    
    # This would require InfluxDB CLI or API access
    # For now, we'll just check if the container is accessible
    if docker exec influxdb influx ping >/dev/null 2>&1; then
        print_status "OK" "InfluxDB is accessible"
    else
        print_status "WARNING" "Cannot access InfluxDB"
    fi
}

check_influxdb_data "Inst_Demand_state" "meter_001"
check_influxdb_data "Inst_Demand_state" "meter_002"

# Check network connectivity
echo ""
echo "6. Checking network connectivity..."

# Check if meters are reachable (if IPs are provided)
meter_1_ip=$(docker inspect xcel_itron2mqtt_meter_001_I2M2G --format='{{range .Config.Env}}{{if eq (index (split . "=") 0) "METER_IP"}}{{index (split . "=") 1}}{{end}}{{end}}' 2>/dev/null || echo "10.28.10.181")
meter_2_ip=$(docker inspect xcel_itron2mqtt_meter_002_I2M2G --format='{{range .Config.Env}}{{if eq (index (split . "=") 0) "METER_IP"}}{{index (split . "=") 1}}{{end}}{{end}}' 2>/dev/null || echo "10.28.10.182")

if [ "$meter_1_ip" != "$meter_2_ip" ]; then
    print_status "OK" "Meters have different IP addresses: $meter_1_ip vs $meter_2_ip"
else
    print_status "ERROR" "Both meters have the same IP address: $meter_1_ip"
fi

# Check environment variables
echo ""
echo "7. Checking environment variables..."

check_env_var() {
    local container=$1
    local var_name=$2
    local description=$3
    
    value=$(docker inspect "$container" --format="table {{.Config.Env}}" 2>/dev/null | grep "$var_name" || echo "")
    if [ -n "$value" ]; then
        print_status "OK" "$description is set"
    else
        print_status "WARNING" "$description is not set"
    fi
}

check_env_var "xcel_itron2mqtt_meter_001_I2M2G" "METER_ID" "Meter 1 ID"
check_env_var "xcel_itron2mqtt_meter_002_I2M2G" "METER_ID" "Meter 2 ID"

# Summary
echo ""
echo "=========================================="
echo "Verification Summary"
echo "=========================================="

echo "To manually verify the setup:"
echo ""
echo "1. Check MQTT topics:"
echo "   mosquitto_sub -h localhost -t 'xcel_itron5_meter_001/+/state' -v"
echo "   mosquitto_sub -h localhost -t 'xcel_itron5_meter_002/+/state' -v"
echo ""
echo "2. Check container logs:"
echo "   docker logs xcel_itron2mqtt_meter_001_I2M2G"
echo "   docker logs xcel_itron2mqtt_meter_002_I2M2G"
echo ""
echo "3. Access Grafana:"
echo "   http://localhost:3000"
echo ""
echo "4. Access InfluxDB:"
echo "   http://localhost:8086"
echo ""
echo "For detailed troubleshooting, see: docs/MULTI_METER_SETUP.md" 