## I2M2G : itron2Mqtt2Grafana

[![Version](https://img.shields.io/badge/version-v3.0-blue.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-2%20meters-green.svg)](https://github.com/your-repo/I2M2G)

This is a branch supports integrating data from two Itron smart meters. The two meters are described as `meter_001` and `meter_002` in `docker-compose.yml` file

## Quick start for 2 Meters

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
