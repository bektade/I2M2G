## I2M2G : Xcel Smart Meter Monitoring using Grafana

I2M2G stands for Itron to MTT to Grafana, which provides a complete solution for monitoring Xcel Energy smart meters using Grafana. This is an extension of [xcel_2iron2mqtt](https://github.com/zaknye/xcel_itron2mqtt) i.e. adding more components such as Telegraph listener to send mqtt messages into InfluxDB and then visualizes the data in real-time (updates every 5 sec) using Grafana.

### influxDB
 <img src="mqtt2grafana/docs/img/influx.png" alt="" width="100%"/>

 ### Grafana Dashbaord
  <img src="mqtt2grafana/docs/img/grafana.png" alt="" width="100%"/>




There are two ways to use this application:

###  Option-A: Interact with Real Meter

- Queries real meters over Wifi to get instantaneous power usage data. 


### Option-B: Interact with Simulator Agent (Energy Launchpad)

  - gets realistic simulated data from energy launchpad's MeterAgentSimulato and publishes it into mqtt.
  - Useful for exploring and testing of smart meter's endpoints using the MeterAgentSimulator and Energy Launchpad.




## Quick start for Real Meter ( OPTION A)

1. clone the repo and add SSL KEYS in mqtt2grafana directory

    <img src="mqtt2grafana/docs/img/tree.jpg" alt="" width="60%"/>
  
    > VERY IMPORTNAT : Add SSL keys in mqtt2grafana directory before doing anything. See the file structure below:

2. cd `mqtt2grafana` and then run `./start_real_meter.sh`
3. Login to InfluxDB at http://localhost:8086  & to Grafana at http://localhost:8086  
4. connect grafana with InfluxDB  [(follow instruction here )](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
5. stop container and delete everything run `./remove_real_meter.sh` 

### Tips 
> - Find  username and passwords in .env file for both InfluxDB & Grafana
> - copy an API token of InfluxDB from `.env` file. 
> - use `DataExplorer` feature in InfluxDB UI
> - use `query Builder` feature to generate Flux queries and use the query to build a dashborad in grafana.


## Quick start for Meter Simulator Setup (OPTION B)


1. `docker compose up` energy launchpad 
 

2. clone this repo and run `start_mqtt.sh` script to start MQTT broker. 

3. cd `simulatedMeter2mqtt` and Run 
    ```
    pipenv shell && pipenv install -r requirements.txt && python main_publishData.py`
    ```

4. Sign in to InfluxDB and Grafana ( same process)


### Tips 
> - check if simulator is working at : `http://<your_host_IP>:8082/swagger/index.html`)
> - Find  username and passwords in .env file for both InfluxDB & Grafana


---
#### Data Flow Architecture

1. **Meter** Data Source
2. **MQTT Broker** receives and routes messages to subscribers
3. **Telegraf** collects data from MQTT topics and sends to InfluxDB
4. **InfluxDB** stores time-series data for historical analysis
5. **Grafana** visualizes real-time and historical data