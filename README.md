## I2M2G : Itron2Mqtt2Grafana with Single meter

[![Version](https://img.shields.io/badge/version-v2.0-blue.svg)](https://github.com/your-repo/I2M2G)
[![Support](https://img.shields.io/badge/support-1%20meter-red.svg)](https://github.com/your-repo/I2M2G)

This is a branch supports integrating data from a single Itron smart meter. The configuration is setup in `docker-compose.yml` file in the `mqtt2grafana` directory.

#### Grafana Dashboard

<img src="mqtt2grafana/docs/img/1m.png" alt="" width="100%"/>

#### InfluxDB

<img src="mqtt2grafana/docs/img/1m_i.png" alt="" width="100%"/>

## Quick start

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
5.  connect grafana with InfluxDB [(follow instruction here )](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
6.  stop container and delete everything run `./remove_real_meter.sh`
