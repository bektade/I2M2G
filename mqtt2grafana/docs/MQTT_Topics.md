## **MQTT Topic Structure**

### **Topic Format**

The application uses this hierarchical topic structure for Home Assistant discovery:

```
homeassistant/{entity_type}/{device_name}/{sensor_name}/{config|state}
```

### **Configuration Topics**

These topics receive the sensor configuration messages:

- `homeassistant/sensor/xcel_itron_5/Instantaneous_Demand/config`
- `homeassistant/sensor/xcel_itron_5/Current_Summation_Received/config`
- `homeassistant/sensor/xcel_itron_5/Current_Summation_Delivered/config`

### **State Topics**

These topics receive the actual sensor data:

- `xcel_itron_5/Instantaneous_Demand/state`
- `xcel_itron_5/Current_Summation_Received/state`
- `xcel_itron_5/Current_Summation_Delivered/state`

### **Device Information Topic**

- `homeassistant/device/energy/xcel_itron_5`

#### **Instantaneous Demand**

- **Purpose**: Real-time power usage monitoring
- **Device Class**: `power`
- **Unit**: `W` (Watts)
- **Update Frequency**: Every 5 seconds
- **Use Case**: Monitor current power consumption

### **Device Entity Creation**

The application creates a **device entity** in Home Assistant that groups all the sensors together:

```json
{
  "name": "Xcel Itron 5",
  "device_class": "energy",
  "state_topic": "homeassistant/device/energy/xcel_itron_5",
  "unique_id": "1234567890123456789012345678901234567890",
  "device": {
    "identifiers": ["1234567890123456789012345678901234567890"],
    "name": "Xcel Itron 5",
    "model": "Itron",
    "sw_version": "3.2.39"
  }
}
```

### **Device Information Sources**

- **Name**: Set to "Xcel Itron 5"
- **Model**: Extracted from meter hardware info (`mfID`)
- **Software Version**: Extracted from meter firmware (`swVer`)
- **Unique ID**: LFDI (Logical Field Device Identifier) from meter
