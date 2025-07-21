# Xcel Energy Monitoring Stack

## **Quick Start**

### **1. Start the Monitoring Stack**

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### **2. Verify Services Are Running**

```bash
# Check service status
docker-compose ps
```

### **4. Test Data Generation**

The simulated meter automatically starts and generates data. You can also run it manually:

```bash
# Run simulated meter locally (recommended for testing)
unset MQTT_SERVER  # Ensure we use localhost
./scripts/run_simulated_meter.sh

# Or run inside Docker network (for production-like testing)
export MQTT_SERVER=mqtt
./scripts/run_simulated_meter.sh

# Run the MQTT subscriber to see raw data
./scripts/run_subscriber.sh
```

**Note**: The simulated meter connects to `localhost:1883` when run locally and `mqtt:1883` when run inside Docker. The script automatically detects the appropriate connection method.

See [Manual Grafana Setup Guide](grafana_manual_setup.md) for detailed instructions.

```bash
unset MQTT_SERVER  # Use localhost
./scripts/run_simulated_meter.sh
```

### **Useful Commands**

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f simulated_meter
docker-compose logs -f telegraf
docker-compose logs -f grafana

# Restart specific service
docker-compose restart simulated_meter

# Access container shell
docker-compose exec grafana bash
docker-compose exec influxdb bash

# Check data in InfluxDB
docker-compose exec influxdb influx query 'from(bucket:"energy_data") |> range(start: -1h)'

# Test MQTT connection locally
unset MQTT_SERVER
./scripts/run_simulated_meter.sh

# Check MQTT topics
./scripts/run_subscriber.sh
```
