# Telegraf Configurations for Smart Meter Data Collection

This directory contains different Telegraf configurations optimized for collecting smart meter telemetry data and writing it to InfluxDB.

## Configuration Files

### 1. `telegraf.conf` (Original)
- **Purpose**: Original configuration with basic MQTT to InfluxDB setup
- **Features**: 
  - Collects data from specific MQTT topics
  - Basic tagging and measurement naming
  - 10-second collection interval
- **Use Case**: General purpose data collection

### 2. `telegraf_2.conf` (Alternative)
- **Purpose**: Enhanced configuration with better organization and additional topics
- **Features**:
  - More comprehensive topic coverage
  - Better tagging structure
  - Includes JSON data format support
  - Catch-all configurations for unknown topics
- **Use Case**: Comprehensive data collection with fallback options

### 3. `telegraf_telemetry.conf` (Recommended)
- **Purpose**: Specialized configuration optimized for numerical telemetry data
- **Features**:
  - **5-second collection interval** for real-time monitoring
  - **Nanosecond precision** timestamps
  - **Organized by metric type**: Power, Energy, Time, Calculated metrics
  - **Rich tagging** for better data analysis
  - **Optimized for time-series analysis**
- **Use Case**: **Production-ready telemetry collection for time-series analysis**

## Key Differences

| Feature | Original | Alternative | Telemetry |
|---------|----------|-------------|-----------|
| Collection Interval | 10s | 10s | **5s** |
| Timestamp Precision | Default | Default | **Nanoseconds** |
| Metric Organization | Basic | Enhanced | **By Type** |
| Tagging | Minimal | Standard | **Rich** |
| Time-Series Optimization | No | No | **Yes** |

## Data Structure in InfluxDB

### Measurements Created:
- `power_metrics` - Power demand and consumption data
- `energy_metrics` - Energy consumption and production data  
- `time_metrics` - Time period tracking data
- `calculated_metrics` - Derived electrical measurements
- `generic_telemetry` - Catch-all for other numerical data

### Tags Available:
- `metric_type` - Type of measurement (power_demand, energy_consumption, etc.)
- `unit` - Unit of measurement (W, Wh, V, A, etc.)
- `device_class` - Home Assistant device class
- `source` - Data source (smart_meter, simulator)
- `direction` - For energy metrics (received, delivered)
- `measurement` - Specific measurement identifier

## Usage Recommendations

### For Development/Testing:
Use `telegraf.conf` or `telegraf_2.conf`

### For Production Time-Series Analysis:
Use `telegraf_telemetry.conf` - This is optimized for:
- Real-time monitoring (5s intervals)
- Accurate timestamps (nanosecond precision)
- Rich metadata for analysis
- Organized data structure

## Example Queries

### SQL Queries (Legacy InfluxDB 1.x)

#### Power Demand Over Time:
```sql
SELECT mean(value) FROM power_metrics 
WHERE metric_type = 'power_demand' 
GROUP BY time(1m)
```

#### Energy Consumption by Direction:
```sql
SELECT sum(value) FROM energy_metrics 
WHERE metric_type = 'energy_consumption' 
GROUP BY direction, time(1h)
```

#### Real-time Power Monitoring:
```sql
SELECT value FROM power_metrics 
WHERE metric_type = 'power_demand' 
ORDER BY time DESC LIMIT 10
```

### FLUX Queries (InfluxDB 2.x)

#### Power Demand Over Time (1-minute averages):
```flux
from(bucket: "smart_meter_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "power_metrics")
  |> filter(fn: (r) => r.metric_type == "power_demand")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "power_demand_avg")
```

#### Energy Consumption by Direction (hourly totals):
```flux
from(bucket: "smart_meter_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_consumption")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
  |> yield(name: "energy_consumption_hourly")
```

#### Real-time Power Monitoring (latest 10 readings):
```flux
from(bucket: "smart_meter_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "power_metrics")
  |> filter(fn: (r) => r.metric_type == "power_demand")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 10)
  |> yield(name: "latest_power_readings")
```

#### Power vs Energy Comparison:
```flux
import "date"

power_data = from(bucket: "smart_meter_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "power_metrics")
  |> filter(fn: (r) => r.metric_type == "power_demand")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)

energy_data = from(bucket: "smart_meter_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_consumption")
  |> aggregateWindow(every: 5m, fn: sum, createEmpty: false)

join(tables: {power: power_data, energy: energy_data}, on: ["_time"])
  |> yield(name: "power_energy_comparison")
```

#### Energy Net Flow (Received - Delivered):
```flux
received = from(bucket: "smart_meter_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_consumption")
  |> filter(fn: (r) => r.direction == "received")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)

delivered = from(bucket: "smart_meter_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_production")
  |> filter(fn: (r) => r.direction == "delivered")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)

join(tables: {received: received, delivered: delivered}, on: ["_time"])
  |> map(fn: (r) => ({r with net_energy: r._value_received - r._value_delivered}))
  |> yield(name: "net_energy_flow")
```

#### Peak Power Usage Detection:
```flux
from(bucket: "smart_meter_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "power_metrics")
  |> filter(fn: (r) => r.metric_type == "power_demand")
  |> aggregateWindow(every: 15m, fn: max, createEmpty: false)
  |> filter(fn: (r) => r._value > 5000)  // Peak above 5kW
  |> yield(name: "peak_power_usage")
```

#### Daily Energy Consumption Summary:
```flux
import "date"

from(bucket: "smart_meter_data")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_consumption")
  |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({r with day_of_week: date.weekDay(t: r._time)}))
  |> yield(name: "daily_energy_summary")
```

#### Time-based Energy Analysis:
```flux
from(bucket: "smart_meter_data")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_consumption")
  |> aggregateWindow(every: 1d, fn: sum, createEmpty: false)
  |> aggregateWindow(every: 7d, fn: mean, createEmpty: false)
  |> yield(name: "weekly_average_consumption")
```

#### Power Factor Analysis (if available):
```flux
from(bucket: "smart_meter_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "calculated_metrics")
  |> filter(fn: (r) => r.metric_type == "power_factor")
  |> aggregateWindow(every: 5m, fn: mean, createEmpty: false)
  |> filter(fn: (r) => r._value < 0.95)  // Poor power factor
  |> yield(name: "poor_power_factor_events")
```

#### Data Quality Check:
```flux
from(bucket: "smart_meter_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "power_metrics")
  |> filter(fn: (r) => r.metric_type == "power_demand")
  |> aggregateWindow(every: 1m, fn: count, createEmpty: false)
  |> filter(fn: (r) => r._value < 10)  // Less than 10 readings per minute
  |> yield(name: "data_gaps")
```

#### Energy Cost Calculation (example with rate):
```flux
// Assuming $0.12 per kWh
rate_per_kwh = 0.12

from(bucket: "smart_meter_data")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "energy_metrics")
  |> filter(fn: (r) => r.metric_type == "energy_consumption")
  |> aggregateWindow(every: 1h, fn: sum, createEmpty: false)
  |> map(fn: (r) => ({r with cost: r._value * rate_per_kwh / 1000}))  // Convert Wh to kWh
  |> yield(name: "hourly_energy_cost")
```

## Environment Variables Required

All configurations require these environment variables:
- `INFLUX_TOKEN` - InfluxDB authentication token
- `INFLUX_ORG` - InfluxDB organization name  
- `INFLUX_BUCKET` - InfluxDB bucket name

## Switching Configurations

To use a different configuration, update your Docker Compose file:

```yaml
telegraf:
  image: telegraf:latest
  volumes:
    - ./telegraf/telegraf_telemetry.conf:/etc/telegraf/telegraf.conf
  # ... other configuration
``` 