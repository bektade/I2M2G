## I2M2G v2.0 - Single Meter Simulator

This application connects to a smart meter simulator agent running in Energy Launchpad. The `meter2mqtt` service queries the simulator every 5 seconds to collect power usage data, which is then published to MQTT for real-time visualization in Grafana.

### step-1: Quick Start

```bash
./setup.sh
```

This will:

- Detect IP address automatically
- Create `.env` from template
- Start all services in background
- Show meter2mqtt logs

### step-2: Access Dashboards & connect Grafana with InfluxDB

You must manually connect Grafana to InfluxDB after startup. See [how to connect Grafana to InfluxDB](/mqtt2grafana/docs/connect_influxdb_2_grafana.md).

- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB**: http://localhost:8086 (admin/adminpassword)

> Note: Use the credentials from your .env file for InfluxDB connection. The default values are admin/adminpassword.

**Note**: In Grafana, add InfluxDB as a data source. Get the configuration details in `.env` file:

- URL: `http://influxdb:8086`
- Token: `super-secret-key`
- Org: `myorg`
- Bucket: `power_usage`
- Query Language: Flux

## Data Flow

Simulator → meter2mqtt → MQTT → Telegraf → InfluxDB → Grafana
