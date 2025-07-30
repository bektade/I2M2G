# Multi-Meter Setup for I2M2G

This setup now supports **2 meters** running simultaneously in separate containers.

## Configuration

### Meters Configuration (`meters.yml`)
The meters are configured in `meters.yml`:
- **Meter 1**: Main House Meter (10.28.10.181:8081)
- **Meter 2**: Garage Meter (10.28.10.182:8081)

### Docker Services
Each meter runs in its own container:
- `xcel_itron2mqtt_meter_001_I2M2G` - Main House Meter
- `xcel_itron2mqtt_meter_002_I2M2G` - Garage Meter

### MQTT Topics
Each meter publishes to unique topics:
- Meter 1: `xcel_itron5_meter_001/sFDI/Power_Demand/state`
- Meter 2: `xcel_itron5_meter_002/sFDI/Power_Demand/state`

## Usage

### Starting the System
```bash
./start_real_meter_linx.sh
```

This will:
1. Generate SSL keys if needed
2. Create `.env` file
3. Start all services including both meter containers
4. Show logs from both meters

### Viewing Logs
```bash
# View logs from both meters
docker logs -f xcel_itron2mqtt_meter_001_I2M2G xcel_itron2mqtt_meter_002_I2M2G

# View logs from specific meter
docker logs -f xcel_itron2mqtt_meter_001_I2M2G
docker logs -f xcel_itron2mqtt_meter_002_I2M2G
```

### Stopping Services
```bash
docker compose --profile real_meter down
```

## Data Flow

1. **Meter Containers**: Each meter connects to its respective smart meter via SSL
2. **MQTT Broker**: Both meters publish data to the same MQTT broker with unique topics
3. **Telegraf**: Collects data from both meter topics and writes to InfluxDB
4. **Grafana**: Visualizes data from both meters in real-time

## Adding More Meters

To add more meters:
1. Edit `meters.yml` to add new meter configuration
2. Add a new service in `docker-compose.yml` following the pattern
3. Update `telegraf/telegraf.conf` to include the new meter's topic

## Troubleshooting

### Check Meter Status
```bash
docker ps | grep xcel_itron2mqtt
```

### Check MQTT Messages
```bash
# Install mosquitto-clients if needed
docker exec mosquitto mosquitto_sub -t "xcel_itron5_+/sFDI/Power_Demand/state" -v
```

### Check InfluxDB Data
Access Grafana at http://localhost:3000 and check the power_usage measurement. 