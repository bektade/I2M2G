## I2M2G - Single Meter Simulator

This application connects to a smart meter simulator agent running in Energy Launchpad. The `meter2mqtt` service queries the simulator every 5 seconds to collect power usage data, which is then published to MQTT for real-time visualization in Grafana.

## Quick Start

### step-1: start services


**For macOS:**
```bash
./start-mac.sh
```

**For Linux:**
```bash
./start-linux.sh
```

**stop services:**
```bash
./stop.sh
```


### step-2: Access Dashboards & connect Grafana with InfluxDB

You must manually connect Grafana to InfluxDB after startup. See [how to connect Grafana to InfluxDB](/mqtt2grafana/docs/connect_influxdb_2_grafana.md).

- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086 (admin/adminpassword)

> Note: Use the credentials from your .env file for InfluxDB connection. The default values are admin/adminpassword.

### Tips 
> - check if simulator is working at : `http://<your_host_IP>:8082/swagger/index.html`)
> - Find  username and passwords in .env file for both InfluxDB & Grafana

