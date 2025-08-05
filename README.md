## Itron2Grafana  -  Xcel Itron Meter Monitoring using fully automated realtime dashboard 

I2M2G stands for Itron to MTT to Grafana, which provides a complete solution for monitoring Xcel Energy smart meters using Grafana. This is an extension of [xcel_2iron2mqtt](https://github.com/zaknye/xcel_itron2mqtt) i.e. adding more components such as Telegraph listener to send mqtt messages into InfluxDB and then visualizes the data in real-time (updates every 5 sec) using Grafana.

### Getting Started:

The application on this repo has many features. It enables to work with a real meter or a meter simulator agent. Checkout the branches depending on what you want to do.

To work with :

- simulator checkout `feature/meter-simulator` branch.

- single real meter checkout `feature/han-single-meter` branch.

- two real meters checkout `feature/han-two-meters` branch.


## Architecture 
<img src="mqtt2grafana/docs/img/arch.png" alt="" width="100%"/>

#### Grafana Dashbaord

  <img src="mqtt2grafana/docs/img/grafana.png" alt="" width="100%"/>

#### influxDB

 <img src="mqtt2grafana/docs/img/influx.png" alt="" width="100%"/>

### Tips

> - check if simulator is working at : `http://<your_host_IP>:8082/swagger/index.html`)
> - Find username and passwords in .env file for both InfluxDB & Grafana

