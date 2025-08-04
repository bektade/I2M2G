## I2M2G : itron2Mqtt2Grafana

[![Version](https://img.shields.io/badge/version-v3.0-blue.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-2%20meters-green.svg)](https://github.com/your-repo/I2M2G)

This is a branch supports integrating data from two Itron smart meters. The two meters are described as `meter_001` and `meter_002` in `docker-compose.yml` file

## Quick start for 2 Meters

### 🚀 Streamlined Workflow (Recommended)

**Step 1: Clone Repository**

```bash
git clone -b feature/han-two-meters --single-branch <git url>
cd I2M2G/mqtt2grafana
```

**Step 2: Setup and Start Two-Meter Stack**

```bash
# Show all available commands
make help

# Setup environment and start everything
make setup

# Monitor the data flow
make monitor

# Check status
make status

# View logs
make logs-meter-001  # Meter 001 (Main House) logs
make logs-meter-002  # Meter 002 (Garage) logs
make logs-telegraf   # telegraf logs
make logs-influx     # influxdb logs

# Pause services (preserves data)
make pause

# Resume services
make resume

# Stop and clean up
make stop

# Restart everything
make restart

# Complete cleanup (removes all data)
make clean
```

**Step 3: SSL Keys Management**

```bash
# Check if SSL keys exist
make check-keys

# Generate SSL keys for meter authentication
make generate-keys
```

**Step 4: Automatically Connect Grafana to InfluxDB and Create Two-Meter Dashboard**

```bash
# Automatically connect InfluxDB to Grafana and create two-meter dashboard
make connect-grafana
```

This will automatically connect grafana with influxDB and will create a real-time dashbaord with separate panels for each meter: `meter_001` and `meter_002`.

**Step 5: Access Dashboards**

After running `make setup`, the script will display the service endpoints using your meter IP:

- **Grafana**: http://YOUR_METER_IP:3000 (admin/admin)
- **InfluxDB**: http://YOUR_METER_IP:8086 (admin/adminpassword)


**Step 6: Pause/Resume or Cleanup**

**Pause/Resume (Recommended for daily use):**
```bash
# Pause services (preserves all data)
make pause

# Resume services later
make resume
```

**Complete Cleanup (Use when you want to start fresh):**
```bash
# Stop I2M2G and clean everything
make stop

# Complete cleanup (removes all data)
make clean
```

**Note:** When services are paused, Grafana will show zero values for the time period when no data was being collected.

### 📋 Manual Workflow (Legacy)

1.  clone this branch:

    ```
    git clone -b feature/han-two-meters --single-branch <git url>
    ```

2.  Copy certs in mqtt2grafana folder

    > VERY IMPORTNAT : Add SSL keys in mqtt2grafana directory before doing anything. See the file structure below:

    <img src="mqtt2grafana/docs/img/tree.jpg" alt="" width="60%"/>

3.  cd `mqtt2grafana` && `./start_real_meter_linux.sh`

4.  Login to InfluxDB at http://localhost:8086 & to Grafana at http://localhost:8086
5.  connect grafana with InfluxDB [(follow instruction here )](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
6.  stop container and delete everything run `./remove_real_meter.sh`

### Tips

> - Find username and passwords in .env file for both InfluxDB & Grafana
> - copy an API token of InfluxDB from `.env` file.
> - use `DataExplorer` feature in InfluxDB UI
> - use `query Builder` feature to generate Flux queries and use the query to build a dashborad in grafana.

### Tips for changing MQTT TOPIC

- To change MQTT topic prefix, simply upadte the `env.template` file's `"MQTT_TOPIC_PREFIX"` under `"MQTT Configuration"`
- To change what you are pulling from smart meters, change `.yaml` files under `xcel_itron2mqtt>configs`
- Tweak telegraph.conf file to ensure proper collection of data from MQTT server to write to InfluxDB (If you notice data is not coming into InfluxDB)









