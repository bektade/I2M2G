# Setup for Simulator

When working with meterSimulator, need to specify `host IP` which will be part of the simulated meter endpoint url.

We don't need to specify:

- IP address of smart meter
- security certificates (LFDIs)

Follow steo by step guide below:

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

#### Step-3: InfluxDB

- Login into InfluxDB dashboard at http://localhost:8086
- create an API token to link InfluxDB with Grafana. (Follow instruction [here](/mqtt2grafana/docs/api_token.md))

  > use `DataExplorer` feature in InfluxDB UI, to confirm data is coming into InfluxDB
  > use `query Builder` feature in InfluxDB and use the query to build a dashborad in grafana.

  > **Note**: login username & passwords are in `.env`.

#### Step-4: Grafana

- Login into Grafana dashboard at http://localhost:8086
- connect grafana with InfluxDB follow [instructions](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
- create visualization & customize it.
