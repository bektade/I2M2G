## I2M2G - Meter Simulator

[![Version](https://img.shields.io/badge/version-v1.0-teal.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-%20metersimulator-green.svg)](https://github.com/your-repo/I2M2G)

This application connects to a smart meter simulator agent running in Energy Launchpad. The `meter2mqtt` service queries the simulator every 5 seconds to collect power usage data, which is then published to MQTT for real-time visualization in Grafana.

## Quick Start

1. Git clone

   ```
   # clone this branch
   git clone -b <branch-name> --single-branch <URL>

   # clone energy launchpad (repo)
   git clone <energy launchpad repo url>
   ```

2. Start services

- Start meter simulator:

  ```
  # cd to launchped dir
  cd launchpad

  # start simulator
  docker compose up
  ```

- start I2M2G

  ```bash
  # mac
  ./start-mac.sh
  ```

  ```bash
  # linux
  ./start-linux.sh
  ```

3. Access Dashboards & connect Grafana with InfluxDB

- You must manually connect Grafana to InfluxDB after startup. See [how to connect Grafana to InfluxDB](/mqtt2grafana/docs/connect_influxdb_2_grafana.md).

  - **Grafana**: http://localhost:3000 (admin/admin)
  - **InfluxDB**: http://localhost:8086 (admin/adminpassword)

  > Note: Use the credentials from your .env file for InfluxDB connection. The default values are admin/adminpassword.

  ### Tips

  > - check if simulator is working at : `http://<your_host_IP>:8082/swagger/index.html`)
  > - Find username and passwords in .env file for both InfluxDB & Grafana

4. Cleaning up

   ```bash
   # stop I2m2G - run shell script

   ./stop.sh


   # stop simulator ( run inside launchpad dir)
   docker compose down -vv
   ```
