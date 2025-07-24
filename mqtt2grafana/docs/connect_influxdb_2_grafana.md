## Connect Grafana to InfluxDB

1. Open grafana at http://localhost:3000 and then go to Menu > Add new Connection > search for InfluxDB

   <img src="./img/connect.png" alt="" width="100%"/>
   <img src="./img/add.png" alt="" width="100%"/>

2. Enter configurations

   > **Note**: Look at `Docker-compose.yml` & `.env` to copy some of configuration details.

   > [How to get API token](/mqtt2grafana/docs/api_token.md)

   <img src="./img/1.png" alt="" width="100%"/>
   <img src="./img/2.png" alt="" width="100%"/>
   <img src="./img/5.png" alt="" width="100%"/>

3. Query Builder

   <img src="./img/3.png" alt="" width="100%"/>
   <img src="./img/4.png" alt="" width="100%"/>
