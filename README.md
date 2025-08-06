<img src="mqtt2grafana/docs/img/h2.png" alt="Project Header" width="100%"/>

---

[![Support](https://img.shields.io/badge/support-1%20meter-red.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-2%20meters-green.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-%20metersimulator-green.svg)](https://github.com/your-repo/I2M2G)

# Automated Real-Time Itron Smart Meter Monitoring

This repository provides a fully automated, containerized solution for real-time monitoring of Xcel Energy Itron smart meters using **MQTT**, **InfluxDB**, and **Grafana**.

It extends the original [xcel_itron2mqtt](https://github.com/zaknye/xcel_itron2mqtt) project by adding new features and streamlined automation.

## ✨ New Features

| Feature                       | Description                                                                                    |
| ----------------------------- | ---------------------------------------------------------------------------------------------- |
| **MQTT Data Ingestion**       | Reads smart meter data from an MQTT using a Telegraf.                                          |
| **InfluxDB Integration**      | Store readings in a time-series database (InfluxDB) for querying and analysis.                 |
| **Grafana Dashboards**        | Auto-configure dashboards for real-time data visualization (every 5 seconds).                  |
| **Multi-Meter Support**       | Supports monitoring of one or multiple physical smart meters.                                  |
| **Simulator Support**         | Supports working with Energy launchpad smart meter simulator agent.                            |
| **Dockerized Deployment**     | All services (MQTT, Telegraf, InfluxDB, Grafana) are containerized using Docker.               |
| **Environment Configuration** | Centralized `.env` file for managing MQTT, database, and Grafana credentials.                  |
| **Makefile Automation**       | Simplified common tasks like setup, pause/resume, and teardown using `make` commands and bash. |

## Architecture

<img src="mqtt2grafana/docs/img/arch.png" alt="" width="100%"/>

#### Grafana Dashbaord

  <img src="mqtt2grafana/docs/img/grafana.png" alt="" width="100%"/>

  <img src="mqtt2grafana/docs/img/grafana_b.png" alt="" width="100%"/>

   <img src="mqtt2grafana/docs/img/1m.png" alt="" width="100%"/>

#### InfluxDB

 <img src="mqtt2grafana/docs/img/influx.png" alt="" width="100%"/>

## Getting Started

To use a specific setup:

- **Simulator**: switch to the `feature/meter-simulator` branch
- **Single Real Meter**: switch to `feature/han-single-meter`
- **Two Real Meters**: switch to `feature/han-two-meters`
