## I2M2G : Xcel Smart Meter Monitoring using Grafana

I2M2G stands for Itron to MTT to Grafana, which provides a complete solution for monitoring Xcel Energy smart meters using Grafana. Here's how this repo organized:

- **mqtt2grafana/**:

  - Is an extension of [xcel_2iron2mqtt](https://github.com/zaknye/xcel_itron2mqtt) i.e. adding more components such as Telegraph listener to send mqtt messages into InfluxDB and then visualizes the data in real-time (updates every 5 sec) using Grafana.

- **simulatedMeter2Mqtt/**:

  - gets realistic simulated data from energy launchpad's MeterAgentSimulato and publishes it into mqtt.
  - Useful for exploring and testing of smart meter's endpoints using the MeterAgentSimulator and Energy Launchpad.
  - If you are using meter simulator [read setup guide.](/simulatedMeter2mqtt/README.SIMULATOR.md)

- **realMeter/**:

  - Contains code to get data from real meters and publish to mqtt.
  - utlizes IEEE 20230.5 protocol to discover smart meters over HAN (Home Area Network) and get data from it.
  - If you are using real meter [read setup guide.](/realMeter2mqtt/README.RealMeter.md)

---
