## I2M2G v3.0 :  Support 2 meters

> This is a branch frm master, created to fix the current issue in the master branch ( UNABLE TO PUBLISH TO MQTT TOPIC).
> Thus this branch is only to work with real meter (Option A)

## Quick start for Real Meter 

1.  clone the repo
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