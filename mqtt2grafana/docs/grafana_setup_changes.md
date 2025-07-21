# Grafana Setup Changes - Manual UI vs Hardcoded Provisioning

## **Overview:**

This document explains the changes made to switch from hardcoded Grafana provisioning to manual UI-based setup. This approach provides better control, easier troubleshooting, and eliminates token-related issues.

---

## **What Changed**

### **1. Removed Hardcoded Provisioning Files**

**Deleted Files:**

- `grafana/provisioning/datasources/influxdb.yaml`
- `grafana/provisioning/dashboards/dashboard.yaml`

**Why:** These files were causing issues with incorrect tokens and inflexible configuration.

### **2. Updated Docker Compose Configuration**

**Modified:** `docker-compose.yml`

**Changes:**

- Removed provisioning volume mounts:
  ```yaml
  # REMOVED:
  - ./grafana/provisioning:/etc/grafana/provisioning
  - ./grafana/dashboards:/var/lib/grafana/dashboards
  ```
- Kept only the persistent data volume:
  ```yaml
  # KEPT:
  - grafana_data:/var/lib/grafana
  ```

### **3. Created Manual Setup Guide**

**New File:** `docs/grafana_manual_setup.md`

**Features:**

- Step-by-step UI setup instructions
- Correct InfluxDB connection parameters
- Dashboard import guidance
- Troubleshooting section
- Example Flux queries

### **4. Updated Documentation**

**Modified Files:**

- `docs/monitoring_stack.md` - Added reference to manual setup
- `scripts/setup_env.sh` - Added setup instructions

---

## **Benefits of Manual Setup**

### **Advantages:**

1. **Better Control**

   - See exactly what's being configured
   - No hidden configuration files
   - Easy to modify settings

2. **Easier Troubleshooting**

   - Clear error messages in UI
   - Visual confirmation of settings
   - No token mismatches

3. **Learning Experience**

   - Better understanding of Grafana
   - Learn InfluxDB connection process
   - Understand dashboard configuration

4. **Flexibility**
   - Easy to change data source settings
   - Simple to add new dashboards
   - No need to restart containers for config changes

### **Disadvantages:**

1. **Manual Steps Required**

   - Need to set up data source manually
   - Dashboard import requires manual steps
   - Not fully automated

2. **Repetition for New Deployments**
   - Setup steps must be repeated
   - No automatic configuration

---

## **Setup Process Comparison**

### **Old Way (Hardcoded):**

```bash
# Start containers
docker-compose up -d

# Hope provisioning works
# Debug if it doesn't
```

### **New Way (Manual):**

```bash
# Start containers
docker-compose up -d

# Follow manual setup guide
# 1. Access Grafana UI
# 2. Add InfluxDB data source
# 3. Import dashboard
# 4. Verify data flow
```

---

## **Migration Guide**

### **For Existing Users:**

1. **Backup Current Configuration:**

   ```bash
   # If you have custom dashboards, export them
   # Save any custom data source configurations
   ```

2. **Update to New Version:**

   ```bash
   git pull origin main
   ```

3. **Restart Services:**

   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Follow Manual Setup:**
   - See `docs/grafana_manual_setup.md`
   - Re-add data source manually
   - Re-import dashboards

### **For New Users:**

1. **Run Setup Script:**

   ```bash
   ./scripts/setup_env.sh
   ```

2. **Start Services:**

   ```bash
   docker-compose up -d
   ```

3. **Follow Manual Setup Guide:**
   - See `docs/grafana_manual_setup.md`

---

## **Troubleshooting**

### **Common Issues:**

1. **"No Data" in Grafana:**

   - Verify InfluxDB connection
   - Check token is correct: `my-super-secret-auth-token`
   - Test connection in Grafana UI

2. **Dashboard Import Fails:**

   - Ensure data source name matches exactly
   - Check JSON file is valid
   - Try importing with different data source name

3. **Connection Refused:**
   - Verify InfluxDB is running: `docker-compose ps`
   - Check URL: `http://influxdb:8086`
   - Verify organization: `myorg`

### **Useful Commands:**

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs grafana
docker-compose logs influxdb

# Test InfluxDB connection
docker-compose exec influxdb influx query 'from(bucket:"energy_data") |> range(start: -1h)'

# Restart services
docker-compose restart grafana influxdb
```

---

## **Future Considerations**

### **For Production:**

1. **Automation Options:**

   - Consider using Grafana API for automation
   - Implement backup/restore procedures
   - Use configuration management tools

2. **Security:**

   - Change default passwords
   - Use environment variables for sensitive data
   - Implement proper authentication

3. **Monitoring:**
   - Add health checks
   - Monitor dashboard performance
   - Set up alerts

### **For Development:**

1. **Quick Setup:**

   - Consider creating setup scripts
   - Document common configurations
   - Share dashboard templates

2. **Testing:**
   - Test with different data sources
   - Validate dashboard functionality
   - Check performance with large datasets

---

## **Conclusion**

The switch to manual UI-based Grafana setup provides better control and reliability, especially for development and testing environments. While it requires more initial setup, it eliminates the token and configuration issues that were common with hardcoded provisioning.

The manual approach is particularly beneficial for:

- **Development environments** where you need to experiment
- **Learning scenarios** where understanding the setup process is important
- **Troubleshooting** where you need to see exactly what's happening

For production environments, you may want to consider implementing automated provisioning using Grafana's API or configuration management tools.
