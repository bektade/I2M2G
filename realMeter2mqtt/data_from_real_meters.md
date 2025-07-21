# Working with Real Smart Meters

This guide explains how to connect to and retrieve data from actual Xcel Energy smart meters over your WiFi network.

## Overview

Smart meters communicate using the Smart Energy Profile (SEP) 2.0 protocol over TLS-secured connections. Each meter has a unique identifier and requires proper authentication to access its data.

## Prerequisites

1. **Xcel Energy Enrollment**: You must be enrolled in Xcel Energy's smart meter program
2. **Network Access**: Your computer must be on the same WiFi network as the smart meter
3. **Approved LFDI**: Your Long Field Device Identifier must be approved by Xcel Energy
4. **Certificate Authentication**: Valid TLS certificates for secure communication

## Setup Process 

### Step 1: Generate Certificates and LFDI

```bash
# Run the automated setup script
./setup_real_meter.sh

# Or manually generate certificates
./scripts/generate_keys.sh
```

This creates:
- `certs/.cert.pem` - Your TLS certificate
- `certs/.key.pem` - Your private key
- LFDI string for Xcel registration

### Step 2: Register with Xcel Energy

1. Go to [Xcel Energy Launchpad](https://my.xcelenergy.com/MyAccount/s/meters-and-devices/)
2. Click "Add a Device"
3. Enter your LFDI (40-character hex string)
4. Wait for approval (24-48 hours)

### Step 3: Configure Your Environment

Create or update your `.env` file:

```bash
# Copy template
cp env.template .env

# Edit .env with your meter details
METER_IP=192.168.1.100    # Your specific meter's IP
METER_PORT=8081           # Usually 8081
CERT_PATH=/opt/xcel_itron2mqtt/certs/.cert.pem
KEY_PATH=/opt/xcel_itron2mqtt/certs/.key.pem
```

#### Understanding the `/opt/` Path

The `/opt/` path refers to the **container's internal filesystem** when running in Docker, not your local machine's filesystem.

**How Volume Mounting Works:**
```yaml
# In docker-compose.yml
volumes:
  - certs:/opt/xcel_itron2mqtt/certs
```

This means:
- **Host side**: Your certificates are in `./certs/` (relative to your project directory)
- **Container side**: They're mounted at `/opt/xcel_itron2mqtt/certs/`

**Path Examples:**

| Environment | CERT_PATH | KEY_PATH |
|-------------|-----------|----------|
| **Docker Container** | `/opt/xcel_itron2mqtt/certs/.cert.pem` | `/opt/xcel_itron2mqtt/certs/.key.pem` |
| **Local Development** | `./certs/.cert.pem` | `./certs/.key.pem` |

**Why This Design?**
1. **Container Isolation**: Each container has its own filesystem
2. **Standard Location**: `/opt/` is the conventional place for application files in Linux
3. **Consistent Paths**: The application always looks in the same location inside the container

**If Running Locally (Not Docker):**
If you run `main.py` directly on your machine, you would use:
```bash
CERT_PATH=./certs/.cert.pem
KEY_PATH=./certs/.key.pem
```

But since the Docker setup is the recommended approach, the container paths (`/opt/...`) are what you specify in your `.env` file. The volume mounting handles the translation between your local `certs/` directory and the container's `/opt/xcel_itron2mqtt/certs/` directory automatically.

### Step 4: Start the Application

```bash
# For real meter
docker-compose --profile real_meter up -d

# For simulated meter (testing)
docker-compose up -d
```

## Network Architecture

### Multiple Meters on Same Network

**Important**: If you have multiple smart meters on the same WiFi network (common in apartment buildings, condos, etc.), you need to specify the exact IP address of your approved meter.

```
Your WiFi Network
├── Your Computer (192.168.1.50)
├── Your Meter (192.168.1.100) ← APPROVED
├── Neighbor's Meter (192.168.1.101) ← NOT APPROVED
├── Neighbor's Meter (192.168.1.102) ← NOT APPROVED
└── ... (up to 48 meters)
```

### Automatic vs Manual IP Discovery

**Automatic Discovery (mDNS)**:
- Uses `_smartenergy._tcp.local.` service discovery
- May connect to wrong meter if multiple exist
- **Not recommended** for multi-meter environments

**Manual IP Specification**:
- Set `METER_IP` in your `.env` file
- Ensures connection to your specific approved meter
- **Recommended** for multi-meter environments

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "Connection Refused" or "Timeout"

**Symptoms**: Application can't connect to meter

**Causes**:
- Wrong IP address
- Meter not on network
- Firewall blocking connection
- Wrong port number

**Solutions**:
```bash
# Check if meter is reachable
ping 192.168.1.100

# Test port connectivity
telnet 192.168.1.100 8081

# Verify your meter's IP in router admin
# Look for devices with names like "ITRON" or "SMARTMETER"
```

#### 2. "Certificate Error" or "Authentication Failed"

**Symptoms**: Connection established but authentication fails

**Causes**:
- LFDI not approved by Xcel
- Wrong certificate files
- Certificate expired
- Wrong meter (approved different meter)

**Solutions**:
```bash
# Verify LFDI approval status
# Check Xcel Energy Launchpad dashboard

# Regenerate certificates if needed
./scripts/generate_keys.sh

# Verify certificate files exist
ls -la certs/
# Should show: .cert.pem and .key.pem

# Check certificate validity
openssl x509 -in certs/.cert.pem -text -noout
```

#### 3. "Wrong Meter" or "Unauthorized Access"

**Symptoms**: Connects to different meter than expected

**Causes**:
- Multiple meters on network
- Automatic discovery picking wrong meter
- Wrong IP address specified

**Solutions**:
```bash
# 1. Find your specific meter's IP
# Check router admin panel for device names
# Look for your meter's serial number or address

# 2. Set specific IP in .env
METER_IP=192.168.1.100  # Your meter's actual IP

# 3. Disable automatic discovery
# Leave METER_IP empty to use mDNS, or set specific IP
```

#### 4. "No Data Received" or "Empty Responses"

**Symptoms**: Connected but no energy data

**Causes**:
- Meter not reporting data
- Wrong endpoint configuration
- Network connectivity issues
- Meter in sleep mode

**Solutions**:
```bash
# Check meter status in Xcel app
# Verify meter is actively reporting

# Test with different endpoints
# Check logs for specific error messages

# Verify network stability
ping -c 10 192.168.1.100
```

#### 5. "mDNS Discovery Issues"

**Symptoms**: Automatic discovery fails or finds wrong meter

**Causes**:
- Multiple meters responding
- Network multicast issues
- Firewall blocking mDNS

**Solutions**:
```bash
# Use manual IP instead
# Set METER_IP in .env file

# Or troubleshoot mDNS
# Check if _smartenergy._tcp.local. is working
dns-sd -B _smartenergy._tcp.local.
```

### Debugging Steps

#### 1. Verify Network Setup

```bash
# Check your network
ifconfig | grep inet

# Scan for smart meters (if you know their naming pattern)
nmap -sn 192.168.1.0/24 | grep -i itron

# Test connectivity to your meter
nc -zv 192.168.1.100 8081
```

#### 2. Verify Certificate Setup

```bash
# Check certificate files
ls -la certs/

# Verify certificate content
openssl x509 -in certs/.cert.pem -text -noout | head -20

# Check private key
openssl rsa -in certs/.key.pem -check
```

#### 3. Test Connection Manually

```bash
# Test TLS connection to meter
openssl s_client -connect 192.168.1.100:8081 \
  -cert certs/.cert.pem \
  -key certs/.key.pem \
  -servername 192.168.1.100
```

#### 4. Check Application Logs

```bash
# View application logs
docker-compose logs xcel_itron2mqtt

# Or if running locally
python3 main.py
```

### Environment-Specific Issues

#### Apartment Buildings / Condos

**Problem**: Multiple meters on shared network

**Solution**:
1. Find your specific meter's IP address
2. Set `METER_IP` in `.env` file
3. Avoid automatic discovery

#### Corporate Networks

**Problem**: Firewall blocking connections

**Solution**:
1. Contact IT department
2. Request access to meter IP/port
3. Use VPN if necessary

#### Rural Areas

**Problem**: Limited network infrastructure

**Solution**:
1. Ensure stable WiFi connection
2. Consider cellular backup
3. Monitor connection stability

## Best Practices

### Security
- Keep certificates secure and never commit to version control
- Use strong passwords for all services
- Regularly rotate credentials
- Monitor for unauthorized access

### Network
- Use static IP for your meter if possible
- Monitor network stability
- Keep router firmware updated
- Consider network segmentation

### Monitoring
- Set up alerts for connection failures
- Monitor data quality and completeness
- Log all connection attempts
- Track energy usage patterns

### Maintenance
- Regularly test connections
- Update certificates before expiration
- Monitor for meter firmware updates
- Keep application dependencies updated

## Getting Help

If you're still having issues:

1. **Check the logs**: `docker-compose logs xcel_itron2mqtt`
2. **Verify network**: Test connectivity to your meter
3. **Confirm approval**: Check Xcel Energy Launchpad
4. **Test certificates**: Verify they're valid and correct
5. **Contact support**: Use GitHub issues for technical problems

## Example Configuration

Here's a complete `.env` file example:

```bash
# Smart Meter Configuration
METER_IP=192.168.1.100
METER_PORT=8081
CERT_PATH=/opt/xcel_itron2mqtt/certs/.cert.pem
KEY_PATH=/opt/xcel_itron2mqtt/certs/.key.pem

# MQTT Configuration
MQTT_SERVER=mqtt
MQTT_PORT=1883
MQTT_USER=
MQTT_PASSWORD=

# Application Configuration
LOGLEVEL=INFO

# InfluxDB Configuration
INFLUXDB_INIT_USERNAME=admin
INFLUXDB_INIT_PASSWORD=adminpassword
INFLUXDB_INIT_ORG=myorg
INFLUXDB_INIT_BUCKET=energy_data
INFLUXDB_INIT_ADMIN_TOKEN=my-super-secret-auth-token

# Grafana Configuration
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

This configuration ensures you connect to your specific approved meter and avoid issues with multiple meters on the same network. 