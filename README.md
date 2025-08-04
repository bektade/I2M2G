## Itron2Grafana  -  Xcel Smart Meter Monitoring using fully automated realtime dashboard 

[![Version](https://img.shields.io/badge/version-v1.0-teal.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-%20metersimulator-green.svg)](https://github.com/your-repo/I2M2G)



This application connects to a smart meter simulator agent running in Energy Launchpad. The `meter2mqtt` service queries the simulator every 5 seconds to collect power usage data, which is then published to MQTT for real-time visualization in Grafana.

## Quick Start

### 🚀 Streamlined Workflow (Recommended)

**Step 1: Clone Required Repositories**

```bash
# Clone this I2M2G repository
git clone -b <branch-name> --single-branch <URL>

# Clone Energy Launchpad repository (for simulator)
git clone <energy launchpad repo url>
```

**Step 2: Start the Meter Simulator**

```bash
# Navigate to launchpad directory
cd launchpad

# Start the simulator
docker compose up
```

**Step 3: Start I2M2G Stack**

```bash
# Navigate back to I2M2G directory
cd ../I2M2G


# Setup and start everything (detects OS automatically)
make setup


# Pause services (preserves data)
make pause

# Resume services
make resume
```




**Step 4: Automatically Connect Grafana to InfluxDB and Create Dashboard**

```bash
# Automatically connect InfluxDB to Grafana and create power usage dashboard
make connect-grafana
```

This will automatically connect InfluxDB to Grafana, setting up the data source with proper authentication, creates a customized Power Usage Dashboard with real-time visualization. 


**Step 5: Access Dashboards**

- **Grafana**: http://YOUR_HOST_IP:3000 (admin/admin)
- **InfluxDB**: http://YOUR_HOST_IP:8086 (admin/adminpassword)



**Step 6: Pause/Resume or Cleanup**

**Pause/Resume (preserves all data):**
```bash
# Pause services 
make pause

# Resume services later
make resume
```

**Complete Cleanup (deletes data and starts):**
```bash
# Stop I2M2G and clean everything
make stop

# Stop simulator (run inside launchpad dir)
cd ../launchpad
docker compose down -vv
```

**Note:** When services are paused, Grafana will show no data points for the time period when no data was being collected.


## Additional commands 

```bash
# Show all available commands
make help

# Check status
make status

# Monitor the data flow
make monitor

# View logs
make logs-meter    # meter2mqtt logs
make logs-telegraf # telegraf logs
make logs-influx   # influxdb logs

# Stop and clean up
make stop

# Restart everything
make restart

# Complete cleanup (removes all data)
make clean
```


### Tips

  > - Check if simulator is working at: `http://<SIMULATOR_IP>:8082/swagger/index.html`
  > - Find SIMULATOR_IP, username and passwords in .env file for both InfluxDB & Grafana
  > - SIMULATOR_IP = Host IP