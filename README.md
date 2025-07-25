# I2M2G : Xcel Smart Meter Monitoring using Grafana

I2M2G stands for Itron to MTT to Grafana, which provides a complete solution for monitoring Xcel Energy smart meters using Grafana. Here's how this repo organized:

- **mqtt2grafana/**:

  - Is an extension of [xcel_2iron2mqtt](https://github.com/zaknye/xcel_itron2mqtt) i.e. adding more components such as Telegraph listener to send mqtt messages into InfluxDB and then visualizes the data in real-time (updates every 5 sec) using Grafana.

  - Read [setup gude for Mqtt2Grafana](#mqtt2grafana-setup) below.

- **simulatedMeter2Mqtt/**:

  - gets realistic simulated data from energy launchpad's MeterAgentSimulato and publishes it into mqtt.
  - Useful for exploring and testing of smart meter's endpoints using the MeterAgentSimulator and Energy Launchpad.
  - If you are using meter simulator [read setup guide.](#meter-simulator-setup-option-b)

#### Data Flow

1. **Meter** Data Source
2. **MQTT Broker** receives and routes messages to subscribers
3. **Telegraf** collects data from MQTT topics and sends to InfluxDB
4. **InfluxDB** stores time-series data for historical analysis
5. **Grafana** visualizes real-time and historical data

## Setup for Real Meter ( OPTION A)

> When working with real meter, need to the following:
>
> - IP address of smart meter in .env file
> - SSL certificates (LFDIs) needs to be generated or copied.

### Overview of the steps:

1. clone the repo & cd `mqtt2grafana`
2. create `.env` file by running `./scripts/setup_env.sh` ; enter METER_IP address in the prompt and use default values for the rest.
3. Generate SSL keys or copy paste existing keys in `mqtt2grafana` directory
4. Docker compose up the container using `--profile real_meter`
5. Login to InfluxDB dashboard and grafana at local host to connect them and create visuailazation in Grafana.

### Detailed step by step guide:

#### step-1: Clone the repo and Configure Environment

Setup the environment by running:

```bash
./scripts/setup_env.sh

# or
./mqtt2grafana/scripts/setup_env.sh
```

> once .env is created edit meter's IP address in it.

#### step-2: Generate SSL Certificates or Copy existing keys

Place the keys in mqtt2grafana directorty.

```bash
# generate new SSL keys
./scripts/generate_keys.sh
```

```bash
# Retrieve existing SSL Keys
./scripts/generate_keys.sh -p
```

These keys will be saved in the local directory `certs/.cert.pem` and `certs/.key.pem`

#### Step-3: Build and Start Container

```
# run container
cd mqtt2grafana
docker compose --profile real_meter up --build

# see logs from xcel_itron2mqtt_I2M2G
docker logs -f xcel_itron2mqtt_I2M2G

# tear down
docker compose down -vv


# clean up
docker system prune
docker network prune
```

Restart the Stack

```
docker compose down -v
docker compose --profile real_meter up --build
```

#### Step-4: InfluxDB

- Login into InfluxDB dashboard at http://localhost:8086
- create an API token to link InfluxDB with Grafana. (Follow instruction [here](/mqtt2grafana/docs/api_token.md))

  > use `DataExplorer` feature in InfluxDB UI, to confirm data is coming into InfluxDB
  > use `query Builder` feature in InfluxDB and use the query to build a dashborad in grafana.

  > **Note**: login username & passwords are in `.env`.

#### Step-5: Grafana

- Login into Grafana dashboard at http://localhost:8086
- connect grafana with InfluxDB follow [instructions](/mqtt2grafana/docs/connect_influxdb_2_grafana.md)
- create visualization & customize it.

---

## Meter Simulator Setup (OPTION B)

#### Overview of steps to run with simulator:

1. `docker compose up` energy launchpad and open it at `http://<host_IP>:8082/swagger/index.html`

2. clone this repo and run `setup_env.sh` script to setup `mqtt2grafana`

3. cd to `mqtt2grafana` & Run `docker compose up`

4. cd `simulatedMeter2mqtt` and Install dependencies `Pipenv install` and run `python main_simulated_pub.py`

5. Sign in to InfluxDB and Grafana.

> When working with meterSimulator specify:
>
> - `host IP` which will be part of the simulated meter endpoint url.
> - We `don't` need to specify IP address of smart meter and security certificates (LFDIs)

Follow steo by step guide below:

#### STEP-0: RUN ENERGY LAUNCHPAD CONTAINERIZED APPLICATION

- The energy launchpad clinet has Smart meter simulator agent which generates data.
- Will be sending get request to this client and publish the response in MQTT topic.

**The end points are at:**

```
http://<host_IP>:8082/swagger/index.html
```

#### step-1: clone this repo and Configure environment

- run `setup_env.sh` script to setup `mqtt2grafana`

  ```
  ./mqtt2grafana/scripts/setup_env.sh
  ```

  > creates .env file inside mqtt2grafana dir

#### Step-2: Start energy launchpad

- clone energy launchpad repo, cd to the repo and run `docker compose up`

#### Step-3: Setup `simulator2mqtt` - gets data from launchpad and publishes it to `mqtt2grafana`

- cd simulator2mqtt
- Install python dependencies found in `Pipfile` and then,
- run `main_simulated_pub.py`.

  ```
    # cd simulator2mqtt
    # pipenv install -r requirements.txtx

  ```

> GETTING FROM SIMULATOR IS NOT DOCKERIZED. Simply run the python script.

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

---

### some cmds

    cd $(pipenv --venv)

    ipconfig getifaddr en0
