# I2M2G - Smart Meter Monitoring

Simple Docker-based smart meter monitoring with Grafana visualization. Needs energy launchpad running in a separate container which `meter2mqtt` will send get request to it and publish the response to mqtt broker. Telegraph listens to incoming message in MQTT and sends data to InfluxDB. Grafana connects to InfluxDB and viuslizes data in real time (5 sec update).

## Quick Start

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```
   
   This will create the .env file and start the application automatically.

2. **Or run manually:**
   ```bash
   docker-compose up --build
   ```

3. **Access dashboards:**
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **InfluxDB**: http://localhost:8086 (admin/adminpassword)

## What's Included

- **meter2mqtt**: Queries simulator and publishes to MQTT
- **MQTT Broker**: Mosquitto message broker
- **Telegraf**: Collects data from MQTT
- **InfluxDB**: Time-series database
- **Grafana**: Data visualization

## Configuration

The application connects to your simulator at `10.195.251.91:8082` by default.

To change the simulator IP, edit `.env`:
```bash
SIMULATOR_IP=your_simulator_ip
```

## Commands

```bash
# Start services
docker-compose up --build

# View meter2mqtt logs
docker-compose logs -f meter2mqtt

# Stop services
docker-compose down

# Restart meter2mqtt
docker-compose restart meter2mqtt
```

## Data Flow

1. **meter2mqtt** → Queries simulator every 5 seconds
2. **MQTT** → Receives and routes messages
3. **Telegraf** → Collects data every 1 second
4. **InfluxDB** → Stores time-series data
5. **Grafana** → Visualizes real-time data
    
