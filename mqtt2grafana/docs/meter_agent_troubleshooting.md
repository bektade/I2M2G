# Meter Agent Simulator Troubleshooting Guide

This guide helps you troubleshoot common issues with the dockerized meter agent simulator.

## Common Issues and Solutions

### 1. Connection Refused Errors

**Symptoms:**
```
Error: HTTPConnectionPool(host='localhost', port=8082): Max retries exceeded
```

**Cause:** The meter agent simulator is trying to connect to `localhost:8082` instead of the Docker service.

**Solution:**
- Ensure the `METER_HOST` environment variable is set to `simulated_meter` in docker-compose.yml
- Check that the simulated_meter service is running: `docker-compose ps`

### 2. MQTT Connection Issues

**Symptoms:**
```
Failed to connect to MQTT broker: [Errno 111] Connection refused
```

**Cause:** MQTT broker is not ready or network issues.

**Solution:**
- Check MQTT service is running: `docker-compose logs mqtt`
- Verify MQTT_SERVER environment variable is set correctly
- Wait for services to fully start up

### 3. XML Parsing Errors

**Symptoms:**
```
xml.etree.ElementTree.ParseError: no element found
```

**Cause:** The simulated meter is not returning valid XML.

**Solution:**
- Check simulated meter logs: `docker-compose logs simulated_meter`
- Verify the simulated meter is generating proper XML responses
- Check if the meter endpoints are accessible

### 4. Container Startup Order Issues

**Symptoms:**
```
Error: Connection refused to simulated_meter:8082
```

**Cause:** Meter agent simulator starts before simulated meter is ready.

**Solution:**
- The `depends_on` in docker-compose.yml should handle this
- Add health checks or wait logic if needed
- Check service startup order: `docker-compose ps`

## Debugging Commands

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs meter_agent_simulator
docker-compose logs simulated_meter
docker-compose logs mqtt

# Follow logs in real-time
docker-compose logs -f meter_agent_simulator
```

### Test MQTT Connectivity
```bash
# Subscribe to MQTT topics
docker exec -it mosquitto mosquitto_sub -t 'xcel_itron5/+/Power_Demand/state' -v

# Publish test message
docker exec -it mosquitto mosquitto_pub -t 'test/topic' -m 'test message'
```

### Test Meter Endpoints
```bash
# Test simulated meter endpoints
curl http://localhost:8082/sdev
curl http://localhost:8082/upt/0/mr/1/r
```

### Check Container Networking
```bash
# Check if containers can reach each other
docker exec -it meter_agent_simulator ping simulated_meter
docker exec -it meter_agent_simulator curl http://simulated_meter:8082/sdev
```

## Environment Variables

Ensure these environment variables are set correctly in your `.env` file:

```bash
# MQTT Configuration
MQTT_SERVER=mqtt
MQTT_PORT=1883
MQTT_USER=
MQTT_PASSWORD=

# Meter Configuration (for Docker)
METER_HOST=simulated_meter
METER_PORT=8082
```

## Service Dependencies

The correct startup order should be:
1. MQTT Broker (mosquitto)
2. Simulated Meter
3. Meter Agent Simulator
4. Telegraf
5. Grafana

## Common Fixes

### 1. Restart Services
```bash
docker-compose down
docker-compose up -d
```

### 2. Rebuild Containers
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 3. Check Network
```bash
docker network ls
docker network inspect xcel_itron2mqtt_default
```

### 4. Verify Data Flow
1. Check simulated meter is generating data
2. Verify meter agent simulator can connect to simulated meter
3. Confirm MQTT messages are being published
4. Validate Telegraf is collecting data
5. Check Grafana dashboards

## Expected Output

### Successful Meter Agent Simulator Output
```
Meter Agent Simulator
====================
Monitoring meter reading ID: 1
Meter endpoint: simulated_meter:8082
MQTT broker: mqtt:1883
Press Ctrl+C to stop

INFO:__main__:Connecting to MQTT broker at mqtt:1883
INFO:__main__:Connected to MQTT Broker!
{"value": 51500.0, "touTier": 0, "sFDI": "238775901963"}
```

### Successful MQTT Messages
```
xcel_itron5/238775901963/Power_Demand/state 51500.0
```

## Getting Help

If you're still experiencing issues:

1. Check all service logs: `docker-compose logs`
2. Verify environment variables: `docker-compose config`
3. Test individual components
4. Check the main README.md for setup instructions 