# Smart Meter MQTT Troubleshooting Guide

## MQTT Publish Issues - "PUBLISH NOT SUCCESSFUL" Error

If you're experiencing the error message "PUBLISH NOT SUCCESSFUL: Error in sending MQTT payload", here are the possible reasons and troubleshooting steps.

## Possible Reasons for MQTT Publish Issues:

### 1. **MQTT Connection Problems**
- **Connection lost**: MQTT client disconnected from broker
- **Network issues**: Network connectivity problems
- **Broker unavailable**: Mosquitto broker not running or unreachable

### 2. **Authentication/Authorization Issues**
- **Missing credentials**: No username/password if required
- **Invalid credentials**: Wrong username/password
- **Access denied**: Insufficient permissions for the topic

### 3. **Topic/Message Issues**
- **Invalid topic format**: Malformed MQTT topic names
- **Message too large**: Payload exceeds broker limits
- **Retain flag issues**: Problems with retained messages

### 4. **Resource/System Issues**
- **Memory problems**: Insufficient memory for message handling
- **Queue full**: MQTT client message queue is full
- **Timeout issues**: Publish operations timing out

## Troubleshooting Steps:

### 1. **Check MQTT Connection Status**
```python
# Add this before publishing to verify connection
if not self.client.is_connected():
    print(f"MQTT Client disconnected. Reconnecting...")
    self.client.reconnect()
```

### 2. **Verify MQTT Broker Status**
```bash
# Check if Mosquitto is running
docker ps | grep mosquitto

# Check Mosquitto logs
docker logs mqtt2grafana-mosquitto-1
```

### 3. **Test MQTT Connectivity**
```bash
# Test connection to MQTT broker
mosquitto_pub -h localhost -p 1883 -t "test/topic" -m "test message"

# Subscribe to all topics to see what's being published
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

### 4. **Check Network Connectivity**
```bash
# Test if MQTT port is accessible
telnet localhost 1883

# Check Docker network
docker network ls
docker network inspect mqtt2grafana_default
```

### 5. **Check Environment Variables**
Verify these are set correctly:
- `MQTT_SERVER` - MQTT broker address
- `MQTT_PORT` - MQTT broker port (usually 1883)

### 6. **Review Mosquitto Configuration**
Check `mosquitto/config/mosquitto.conf`:
- Ensure `allow_anonymous true` is set
- Check for any access restrictions
- Verify port configuration

### 7. **Debug MQTT Client**
Add these debug lines to your `setup_mqtt` method in `xcelMeter.py`:

```python
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code: {rc}")
    if rc == 0:
        print("Successfully connected to MQTT broker")
    else:
        print(f"Failed to connect to MQTT broker: {rc}")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code: {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published successfully with message ID: {mid}")

def on_log(client, userdata, level, buf):
    print(f"MQTT Log: {buf}")
```

### 8. **Check Message Content**
Before publishing, verify the message format:
```python
# Add this before publish
print(f"Topic: {topic}")
print(f"Message type: {type(message)}")
print(f"Message content: {message}")
print(f"Message length: {len(str(message))}")
```

### 9. **Test with Simple Message**
Try publishing a simple test message:
```python
# Test with minimal payload
test_result = self.client.publish("test/topic", "test")
print(f"Test publish result: {test_result.rc}")
```

### 10. **Review All Logs**
```bash
# Telegraf logs
docker logs mqtt2grafana-telegraf-1

# Mosquitto logs
docker logs mqtt2grafana-mosquitto-1

# Your application logs
docker logs <your-app-container>

# InfluxDB logs
docker logs mqtt2grafana-influxdb-1

# Grafana logs
docker logs mqtt2grafana-grafana-1
```

## Quick Fix Steps:

### Step 1: Restart Services
```bash
# Restart the entire stack
docker-compose down
docker-compose up -d

# Or restart individual services
docker restart mqtt2grafana-mosquitto-1
docker restart mqtt2grafana-telegraf-1
```

### Step 2: Check Connection
```bash
# Verify MQTT broker is accessible
mosquitto_pub -h localhost -p 1883 -t "test" -m "hello"
```

### Step 3: Monitor Traffic
```bash
# Watch MQTT traffic in real-time
mosquitto_sub -h localhost -p 1883 -t "#" -v
```

### Step 4: Test Your Application
```bash
# Run your smart meter application and watch logs
docker logs -f <your-app-container>
```

## Common Error Codes:

| Code | Meaning | Solution |
|------|---------|----------|
| 0 | Success | No action needed |
| 1 | Unacceptable protocol version | Check MQTT version compatibility |
| 2 | Identifier rejected | Check client ID |
| 3 | Server unavailable | Check if broker is running |
| 4 | Bad username or password | Check credentials |
| 5 | Not authorized | Check topic permissions |

## Most Likely Causes:

1. **MQTT client disconnected** - Most common issue
2. **Network connectivity** - Docker networking problems
3. **Broker not running** - Mosquitto service down
4. **Invalid topic format** - Malformed topic names

## Prevention Tips:

1. **Add connection monitoring** to your application
2. **Implement automatic reconnection** logic
3. **Add message validation** before publishing
4. **Monitor broker health** regularly
5. **Use proper error handling** in publish methods

## Debugging Checklist:

- [ ] MQTT broker is running
- [ ] Network connectivity is working
- [ ] Environment variables are set correctly
- [ ] Topic format is valid
- [ ] Message payload is not too large
- [ ] Client is connected before publishing
- [ ] No authentication issues
- [ ] Docker containers can communicate

## Emergency Recovery:

If all else fails:
```bash
# Complete reset
docker-compose down -v
docker system prune -f
docker-compose up -d

# Rebuild if needed
docker-compose build --no-cache
docker-compose up -d
``` 