## I2M2G : Xcel Smart Meter Monitoring using Grafana

I2M2G stands for Itron to MTT to Grafana, which provides a complete solution for monitoring Xcel Energy smart meters using Grafana. Here's how this repo organized:

- **mqtt2grafana/**:

  - Is an extension of [xcel_2iron2mqtt](https://github.com/zaknye/xcel_itron2mqtt) i.e. adding more components such as Telegraph listener to send mqtt messages into InfluxDB and then visualizes the data in real-time (updates every 5 sec) using Grafana.

- **simulatedMeter2Mqtt/**:

  - gets realistic simulated data from energy launchpad's MeterAgentSimulato and publishes it into mqtt.

  - Useful for exploring and testing of smart meter's endpoints using the MeterAgentSimulator and Energy Launchpad.

- **realMeter/**:

  - Contains code to get data from real meters and publish to mqtt.
  - utlizes IEEE 20230.5 protocol to discover smart meters over HAN (Home Area Network) and get data from it.

---

## Use Case 1: Setup for Simulator Data Source

#### step-1: Configure environment

- run `setup_env.sh` script

  ```
  ./mqtt2grafana/scripts/setup_env.sh
  ```

  > creates .env file inside mqtt2grafana dir

#### Step-2: Setup data source `simulator2mqtt`

- `simulator2mqtt` sends get request to meterSimulatorAgent in Energy Launchpad and publishes the response to MQTT topic. To make this work:
- clone energy launchpad repo, cd to the repo and run `docker compose up`
- Install python dependencies found in `Pipfile` and then,
- run `main_simulated_pub.py`.

#### step-3: InfluxDB

- Login into InfluxDB dashboard at http://localhost:8086
- create an API token to link InfluxDB with Grafana. (Follow instruction [here](/mqtt2grafana/docs/api_token.md))

  > use `DataExplorer` feature in InfluxDB UI, to confirm data is coming into InfluxDB
  > use `query Builder` feature in InfluxDB and use the query to build a dashborad in grafana.

  > **Note**: login username & passwords are in `.env`.

#### step-4: Grafana

- Login into Grafana dashboard at http://localhost:8086
- connect grafana with InfluxDB follow [instructions](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
- create visualization & customize it.

## Use Case 2: Setup for Real Meter Data Source

- **realmeter2mqtt:** Use [itron2mqtt3](git@github.com:betkh/itron2mqtt3.git).
