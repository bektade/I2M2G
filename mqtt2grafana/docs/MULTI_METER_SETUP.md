# Multi-Meter Setup Guide

This guide explains how to configure the system to work with multiple smart meters, allowing you to collect and visualize data from separate meters independently.

## Overview

The system is designed to support multiple smart meters with the following architecture:

```
Smart Meter 1 (10.28.10.181) → xcel_itron2mqtt_meter_001 → MQTT Broker → Telegraf → InfluxDB → Grafana
Smart Meter 2 (10.28.10.182) → xcel_itron2mqtt_meter_002 → MQTT Broker → Telegraf → InfluxDB → Grafana
```

## Key Features

- **Separate Meter Identification**: Each meter has a unique `METER_ID` (meter_001, meter_002)
- **Independent IP Addresses**: Each meter connects to a different physical meter IP
- **Meter-Specific MQTT Topics**: All MQTT topics are prefixed with the meter ID
- **Tagged Data Collection**: Telegraf adds meter-specific tags to distinguish data sources
- **Grafana Dashboards**: Separate dashboards can be created for each meter

## Configuration

### 1. Docker Compose Configuration

The `docker-compose.yml` file defines two separate meter services:

```yaml
# Meter 1 (Main House)
xcel_itron2mqtt_meter_001:
  environment:
    - METER_IP=10.28.10.181
    - METER_ID=meter_001
    - METER_NAME=Main House Meter

# Meter 2 (Garage)
xcel_itron2mqtt_meter_002:
  environment:
    - METER_IP=10.28.10.182
    - METER_ID=meter_002
    - METER_NAME=Garage Meter
```

### 2. MQTT Topic Structure

Each meter publishes to meter-specific topics:

**Meter 1 Topics:**
- `xcel_itron5_meter_001/sensor/Instantaneous_Demand/value/state`
- `xcel_itron5_meter_001/sensor/Current_Summation_Delivered/value/state`

**Meter 2 Topics:**
- `xcel_itron5_meter_002/sensor/Instantaneous_Demand/value/state`
- `xcel_itron5_meter_002/sensor/Current_Summation_Delivered/value/state`

### 3. Telegraf Configuration

The `telegraf.conf` file includes separate input plugins for each meter:

```toml
# Meter 1 - Power Demand
[[inputs.mqtt_consumer]]
  topics = ["xcel_itron5_meter_001/sensor/Instantaneous_Demand/value/state"]
  tags = {"meter_id" = "meter_001", "meter_name" = "Main House Meter"}

# Meter 2 - Power Demand  
[[inputs.mqtt_consumer]]
  topics = ["xcel_itron5_meter_002/sensor/Instantaneous_Demand/value/state"]
  tags = {"meter_id" = "meter_002", "meter_name" = "Garage Meter"}
```

## Data Flow

1. **Meter Connection**: Each meter service connects to its assigned IP address
2. **Data Collection**: Meters query their respective endpoints and collect data
3. **MQTT Publishing**: Data is published to meter-specific topics
4. **Telegraf Collection**: Telegraf subscribes to both meter topics
5. **InfluxDB Storage**: Data is stored with meter-specific tags
6. **Grafana Visualization**: Dashboards can filter by meter_id tag

## Adding More Meters

To add additional meters:

1. **Add Docker Service**: Copy the meter service configuration and update:
   - `METER_IP` (new meter IP)
   - `METER_ID` (unique identifier)
   - `METER_NAME` (descriptive name)

2. **Update Telegraf**: Add new input plugins for the meter's topics

3. **Create Grafana Dashboard**: Build dashboards using the meter_id tag

## Troubleshooting

### Common Issues

1. **Same Data from Both Meters**: 
   - Check that `METER_IP` environment variables are different
   - Verify each meter service connects to a different physical meter

2. **Missing Data**:
   - Check MQTT topic subscriptions in Telegraf
   - Verify meter connectivity and credentials

3. **Grafana Not Showing Separate Data**:
   - Ensure queries filter by `meter_id` tag
   - Check that InfluxDB contains data from both meters

### Verification Steps

1. **Check MQTT Topics**:
   ```bash
   mosquitto_sub -h localhost -t "xcel_itron5_meter_001/+/state" -v
   mosquitto_sub -h localhost -t "xcel_itron5_meter_002/+/state" -v
   ```

2. **Check InfluxDB Data**:
   ```sql
   SELECT * FROM "Inst_Demand_state" WHERE "meter_id" = 'meter_001'
   SELECT * FROM "Inst_Demand_state" WHERE "meter_id" = 'meter_002'
   ```

3. **Check Container Logs**:
   ```bash
   docker logs xcel_itron2mqtt_meter_001_I2M2G
   docker logs xcel_itron2mqtt_meter_002_I2M2G
   ```

## Grafana Dashboard Queries

Example queries for creating meter-specific dashboards:

**Meter 1 Power Demand:**
```sql
SELECT "value" FROM "Inst_Demand_state" WHERE "meter_id" = 'meter_001'
```

**Meter 2 Power Demand:**
```sql
SELECT "value" FROM "Inst_Demand_state" WHERE "meter_id" = 'meter_002'
```

**Combined View:**
```sql
SELECT "value", "meter_name" FROM "Inst_Demand_state" GROUP BY "meter_name"
```

## Environment Variables

Key environment variables for multi-meter setup:

| Variable | Description | Example |
|----------|-------------|---------|
| `METER_IP` | IP address of the physical meter | `10.28.10.181` |
| `METER_ID` | Unique identifier for the meter | `meter_001` |
| `METER_NAME` | Human-readable meter name | `Main House Meter` |
| `METER_PORT` | Port for meter communication | `8081` |

## Security Considerations

- Each meter should have its own SSL certificates
- MQTT authentication should be enabled
- Network access should be restricted to necessary IPs only
- Regular security updates for all components 