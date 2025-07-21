# Manual Grafana Setup Guide:

This guide will help you set up Grafana manually through the web UI instead of using hardcoded provisioning files. This approach gives you more control and is easier to troubleshoot.

---

## **Prerequisites**

1. Make sure your Docker containers are running:

   ```bash
   docker-compose up -d
   ```

2. Verify all services are healthy:
   ```bash
   docker-compose ps
   ```

---

## **Step 1: Access Grafana**

1. **Open your browser and go to:** [http://localhost:3000](http://localhost:3000)

2. **Log in with default credentials:**

   - Username: `admin`
   - Password: `adminpassword`

3. **Change the default password** when prompted (recommended for security)

---

## **Step 2: Add InfluxDB Data Source**

1. **Navigate to Data Sources:**

   - Click the **Configuration** icon (gear) in the left sidebar
   - Select **Data Sources**

2. **Add a new data source:**

   - Click **"Add data source"**
   - Search for and select **"InfluxDB"**
   - Click **"Add"**

3. **Configure the InfluxDB connection:**

   - **Name:** `InfluxDB` (or any name you prefer)
   - **URL:** `http://influxdb:8086`
   - **Access:** Select **"Server (default)"**
   - **Version:** Select **"Flux"**
   - **Organization:** `myorg`
   - **Default Bucket:** `energy_data`
   - **Token:** `my-super-secret-auth-token`
   - **TLS Skip Verify:** Check this box (for development)

4. **Test the connection:**
   - Click **"Save & Test"**
   - You should see a green success message

---

## **Step 3: Import the Energy Monitoring Dashboard**

1. **Navigate to Dashboards:**

   - Click the **Dashboards** icon in the left sidebar
   - Click **"Import"**

2. **Import the dashboard:**

   - Click **"Upload JSON file"**
   - Select the file: `grafana/dashboards/energy_monitoring.json`
   - Click **"Load"**

3. **Configure the import:**
   - **Name:** `Energy Monitoring` (or your preferred name)
   - **Folder:** Leave as default or create a new folder
   - **Data Source:** Select your InfluxDB data source
   - Click **"Import"**

---

## **Step 4: Verify Data is Flowing**

1. **Check the dashboard:**

   - You should see your energy monitoring dashboard
   - If panels show "No data", check the following:

2. **Verify data sources:**

   - Go to **Data Sources** → **InfluxDB** → **Explore**
   - Run this query to check for data:
     ```flux
     from(bucket: "energy_data")
       |> range(start: -1h)
       |> filter(fn: (r) => r._measurement == "power_usage")
     ```

3. **Check container logs if no data:**
   ```bash
   docker-compose logs telegraf
   docker-compose logs simulated_meter
   ```

---

## **Step 5: Create Custom Queries (Optional)**

You can create custom panels with these example Flux queries:

### **Real-time Power Usage:**

```flux
from(bucket: "energy_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "power_usage")
```

### **Energy Consumption (24h):**

```flux
from(bucket: "energy_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "energy_consumption")
```

### **Energy Production (24h):**

```flux
from(bucket: "energy_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "energy_production")
```

### **Hourly Average Power:**

```flux
from(bucket: "energy_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "power_usage")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
```

---

## **Troubleshooting**

### **No Data in Grafana:**

1. Check if InfluxDB has data:

   ```bash
   docker-compose exec influxdb influx query 'from(bucket:"energy_data") |> range(start: -1h)'
   ```

2. Verify Telegraf is running:

   ```bash
   docker-compose logs telegraf
   ```

3. Check simulated meter:
   ```bash
   docker-compose logs simulated_meter
   ```

### **Connection Issues:**

1. Verify InfluxDB is accessible:

   ```bash
   curl http://localhost:8086/health
   ```

2. Check the token is correct:
   - The token should be: `my-super-secret-auth-token`
   - You can verify this in your `.env` file

### **Dashboard Import Issues:**

1. Make sure the JSON file is valid
2. Check that the data source name matches exactly
3. Try importing with a different data source name

---

## **Benefits of Manual Setup**

- **More Control:** You can see exactly what's being configured
- **Easier Debugging:** No hidden configuration files
- **Flexibility:** Easy to modify settings through the UI
- **Learning:** Better understanding of how Grafana works
- **No Token Issues:** You can verify the correct token is being used

---

## **Next Steps**

Once your dashboard is working, you can:

1. **Customize panels** by editing them
2. **Add alerts** for high energy usage
3. **Create additional dashboards** for different views
4. **Set up user accounts** for team access
5. **Configure backup** of your dashboards

---

This manual setup approach gives you full control over your Grafana configuration and makes it much easier to troubleshoot any issues!
