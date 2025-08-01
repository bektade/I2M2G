## I2M2G v2.0: Work with single meter. 

> This branch is for working with single meter. 

## Quick start for Real Meter ( OPTION A)

1.  clone the repo
2.  Copy certs in mqtt2grafana folder

    > VERY IMPORTNAT : Add SSL keys in mqtt2grafana directory before doing anything. See the file structure below:

    <img src="mqtt2grafana/docs/img/tree.jpg" alt="" width="60%"/>

3.  cd `mqtt2grafana` && `./start_real_meter_linux.sh`

4.  Login to InfluxDB at http://localhost:8086 & to Grafana at http://localhost:8086
5.  connect grafana with InfluxDB [(follow instruction here )](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
6.  stop container and delete everything run `./remove_real_meter.sh`
