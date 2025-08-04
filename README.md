## Xcel Itron2Grafana - Fully automated Realtime Dashboard

[![Version](https://img.shields.io/badge/version-v2.0-blue.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-1%20meter-red.svg)](https://github.com/your-repo/I2M2G)

This is a branch supports integrating data from a single Itron smart meter. The configuration is setup in `docker-compose.yml` file in the `mqtt2grafana` directory.

#### Grafana Dashboard

<img src="mqtt2grafana/docs/img/1m.png" alt="" width="100%"/>

#### InfluxDB

<img src="mqtt2grafana/docs/img/1m_i.png" alt="" width="100%"/>

## Quick start

### 🚀 Streamlined Workflow (Recommended)

**Step 1: Clone Repository and add SSL Cert**

```bash
git clone -b feature/han-single-meter --single-branch <URL>
cd I2M2G/mqtt2grafana
```



> VERY IMPORTNAT : Add SSL keys in mqtt2grafana directory before doing anything. See the file structure below:

<img src="mqtt2grafana/docs/img/tree.jpg" alt="" width="60%"/>

**Step 2: Setup and Start Real Meter Stack**

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
make logs-meter    # real meter logs
make logs-telegraf # telegraf logs
make logs-influx   # influxdb logs

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

**Step 4: Automatically Connect Grafana to InfluxDB and Create Dashboard**

```bash
# Automatically connect InfluxDB to Grafana and create power usage dashboard
make connect-grafana
```

This will automatically connect grafana with influxdb and cusomize the dashbaord. 


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

1.  clone this branch

    ```
    # git clone -b <branch-name> --single-branch <URL>

    git clone -b feature/han-single-meter --single-branch <URL>
    ```

2.  Copy certs in mqtt2grafana folder

    > VERY IMPORTNAT : Add SSL keys in mqtt2grafana directory before doing anything. See the file structure below:

    <img src="mqtt2grafana/docs/img/tree.jpg" alt="" width="60%"/>

3.  cd `mqtt2grafana` && `./start_real_meter_linux.sh`

4.  Login to InfluxDB at http://localhost:8086 & to Grafana at http://localhost:8086
5.  Manually connect grafana with InfluxDB [(follow instruction here )](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
6.  stop container and delete everything run `./remove_real_meter.sh`





