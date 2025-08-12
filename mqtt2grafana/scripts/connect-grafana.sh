#!/bin/bash

# Script to automatically connect InfluxDB to Grafana and create dashboard
# Uses information from .env file

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=== Auto-connecting InfluxDB to Grafana and Creating Dashboard ==="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please run 'make setup' first to create the .env file"
    exit 1
fi

# Source the .env file to get variables
source .env

# Check if required variables are set
if [ -z "$INFLUXDB_INIT_USERNAME" ] || [ -z "$INFLUXDB_INIT_PASSWORD" ] || [ -z "$INFLUXDB_INIT_ORG" ] || [ -z "$INFLUXDB_INIT_BUCKET" ] || [ -z "$INFLUXDB_INIT_ADMIN_TOKEN" ]; then
    echo -e "${RED}Error: Missing required InfluxDB variables in .env file${NC}"
    exit 1
fi

# Check if Grafana is running
echo "Checking if Grafana is running..."
if ! docker ps | grep -q grafana; then
    echo -e "${RED}Error: Grafana container is not running${NC}"
    echo "Please start the stack first with 'make start' or 'make setup'"
    exit 1
fi

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}Grafana is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: Grafana did not become ready within 30 seconds${NC}"
        exit 1
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Create the data source configuration
echo "Creating InfluxDB data source configuration..."

# Create a temporary JSON file for the data source
cat > /tmp/influxdb-datasource.json << EOF
{
  "name": "InfluxDB",
  "type": "influxdb",
  "url": "http://influxdb:8086",
  "access": "proxy",
  "isDefault": true,
  "jsonData": {
    "version": "Flux",
    "organization": "$INFLUXDB_INIT_ORG",
    "defaultBucket": "$INFLUXDB_INIT_BUCKET"
  },
  "secureJsonData": {
    "token": "$INFLUXDB_INIT_ADMIN_TOKEN"
  }
}
EOF

# Add the data source to Grafana
echo "Adding InfluxDB data source to Grafana..."
response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -u "admin:admin" \
    -d @/tmp/influxdb-datasource.json \
    http://localhost:3000/api/datasources)

# Check if the data source was added successfully
if echo "$response" | grep -q '"id"'; then
    echo -e "${GREEN}Successfully connected InfluxDB to Grafana${NC}"
    echo "Data source details:"
    echo "  - Name: InfluxDB"
    echo "  - URL: http://influxdb:8086"
    echo "  - Query Language: Flux"
    echo "  - Organization: $INFLUXDB_INIT_ORG"
    echo "  - Default Bucket: $INFLUXDB_INIT_BUCKET"
else
    echo -e "${YELLOW}Warning: Data source might already exist or there was an issue${NC}"
    echo "Response: $response"
fi

# Get the data source ID for the dashboard
echo "Getting data source ID..."
datasource_response=$(curl -s -u "admin:admin" http://localhost:3000/api/datasources/name/InfluxDB)
datasource_id=$(echo "$datasource_response" | grep -o '"id":[0-9]*' | cut -d':' -f2)

if [ -z "$datasource_id" ]; then
    echo -e "${RED}Error: Could not get data source ID${NC}"
    exit 1
fi

echo "Data source ID: $datasource_id"

# Create dashboard configuration with Flux query for power demand
echo "Creating dashboard configuration with Flux query..."

cat > /tmp/power-dashboard.json << EOF
{
  "dashboard": {
    "id": null,
    "title": "Power Usage Dashboard",
    "tags": ["power", "meter", "i2m2g"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Instantaneous Power Demand",
        "type": "timeseries",
                          "targets": [
            {
              "refId": "A",
            "query": "from(bucket: \"$INFLUXDB_INIT_BUCKET\")\n  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n  |> filter(fn: (r) => r[\"_measurement\"] == \"Inst_Demand_state\")\n  |> filter(fn: (r) => r[\"_field\"] == \"value\")\n  |> filter(fn: (r) => r[\"host\"] == \"telegraf-host\")\n  |> filter(fn: (r) => r[\"topic\"] == \"homeassistant/sensor/Instantaneous_Demand/value/state\")\n  |> aggregateWindow(every: v.windowPeriod, fn: last, createEmpty: false)\n  |> yield(name: \"last\")",
            "rawQuery": true,
            "datasource": {
              "type": "influxdb",
              "uid": "$datasource_id"
            }
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 100,
              "gradientMode": "opacity",
              "hideFrom": {
                "legend": false,
                "tooltip": false,
                "vis": false
              },
              "lineInterpolation": "solid",
              "lineWidth": 1,
              "pointSize": 5,
              "scaleDistribution": {
                "type": "linear"
              },
              "showPoints": "always",
              "spanNulls": false,
              "stacking": {
                "group": "A",
                "mode": "none"
              },
              "thresholdsStyle": {
                "mode": "off"
              }
            },
            "mappings": [],
            "thresholds": {
              "mode": "absolute",
              "steps": [
                {
                  "color": "green",
                  "value": null
                },
                {
                  "color": "red",
                  "value": 80
                }
              ]
            },
            "unit": "watt"
          },
          "overrides": []
        },
        "gridPos": {
          "h": 10,
          "w": 25,
          "x": 0,
          "y": 0
        },
        "options": {
          "legend": {
            "calcs": ["lastNotNull"],
            "displayMode": "table",
            "placement": "bottom",
            "showLegend": true
          },
          "tooltip": {
            "mode": "single",
            "sort": "none"
          }
        },
        "title": "Instantaneous Power Demand",
        "type": "timeseries"
      }
    ],
    "time": {
      "from": "now-5m",
      "to": "now"
    },
    "timepicker": {},
    "templating": {
      "list": []
    },
    "annotations": {
      "list": []
    },
    "refresh": "5s",
    "schemaVersion": 30,
    "version": 0,
    "links": [],
    "gnetId": null,
    "style": "dark"
  },
  "folderId": 0,
  "overwrite": true
}
EOF

# Create the dashboard
echo "Creating Power Usage Dashboard..."
dashboard_response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -u "admin:admin" \
    -d @/tmp/power-dashboard.json \
    http://localhost:3000/api/dashboards/db)

# Check if dashboard was created successfully
if echo "$dashboard_response" | grep -q '"id"'; then
    dashboard_id=$(echo "$dashboard_response" | grep -o '"id":[0-9]*' | cut -d':' -f2)
    dashboard_url=$(echo "$dashboard_response" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
    
    echo -e "${GREEN}Successfully created Power Usage Dashboard${NC}"
    echo "Dashboard details:"
    echo "  - Title: Power Usage Dashboard"
    echo "  - ID: $dashboard_id"
    echo "  - URL: http://localhost:3000$dashboard_url"
    echo ""
    echo "Dashboard features:"
    echo "  - Real-time power demand visualization"
    echo "  - Flux query for accurate data filtering"
    echo "  - Auto-refresh every 5 seconds"
    echo "  - Watt unit display"
    echo ""
    echo "You can now access:"
    if [ -f ".env" ]; then
        HOST_IP=$(grep SIMULATOR_IP .env | cut -d'=' -f2)
        echo "  - Grafana: http://$HOST_IP:3000 (admin/admin)"
        echo "  - Dashboard: http://$HOST_IP:3000$dashboard_url"
    else
        echo "  - Grafana: http://localhost:3000 (admin/admin)"
        echo "  - Dashboard: http://localhost:3000$dashboard_url"
    fi
else
    echo -e "${YELLOW}Warning: Dashboard creation might have failed${NC}"
    echo "Response: $dashboard_response"
    echo ""
    echo "You can manually create a dashboard in Grafana at: http://localhost:3000"
fi

# Clean up temporary files
rm -f /tmp/influxdb-datasource.json
rm -f /tmp/power-dashboard.json

echo ""
echo "=== Connection and Dashboard Creation Complete ===" 