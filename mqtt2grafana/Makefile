# I2M2G Two-Meter Makefile - Streamlined project management
# Usage: make <target>

# Detect OS and set appropriate variables
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    PLATFORM := mac
else
    PLATFORM := linux
endif

# Default target
.DEFAULT_GOAL := help

.PHONY: help setup start stop restart status logs clean logs-mqtt logs-meter-001 logs-meter-002 logs-influx logs-grafana logs-telegraf monitor connect-grafana pause resume check-keys generate-keys

# Show help
help: ## Show this help message
	@echo "=== I2M2G Two-Meter Project Management ==="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "Platform detected: $(PLATFORM)"
	@echo ""

# Setup environment and start the stack
setup: ## Setup environment and start the complete two-meter stack
	@echo "=== Setting up I2M2G Two-Meter on $(PLATFORM) ==="
	@chmod +x scripts/setup_env.sh
	@chmod +x scripts/generate_keys.sh
	@./scripts/setup_env.sh
	@echo ""
	@echo "=== Checking SSL Keys ==="
	@./scripts/generate_keys.sh -p || echo "No SSL keys found. Run 'make generate-keys' to create them."
	@echo ""
	@echo "=== Starting Two-Meter Stack ==="
	@docker compose --profile real_meter up --build -d
	@echo "Stack started successfully"
	@if [ -f ".env" ]; then \
		HOST_IP=$$(grep SIMULATOR_IP .env | cut -d'=' -f2 | head -1); \
		echo "Grafana: http://$$HOST_IP:3000 (admin/admin)"; \
		echo "InfluxDB: http://$$HOST_IP:8086 (admin/adminpassword)"; \
		echo "Meter 001 IP: 10.28.10.181"; \
		echo "Meter 002 IP: 10.28.10.182"; \
	else \
		echo "Grafana: http://localhost:3000 (admin/admin)"; \
		echo "InfluxDB: http://localhost:8086 (admin/adminpassword)"; \
	fi

# Start the stack (assumes .env exists)
start: ## Start the Docker stack
	@echo "=== Starting I2M2G Two-Meter Stack ==="
	@docker compose --profile real_meter up --build -d
	@echo "Stack started successfully"
	@if [ -f ".env" ]; then \
		HOST_IP=$$(grep SIMULATOR_IP .env | cut -d'=' -f2 | head -1); \
		echo "Grafana: http://$$HOST_IP:3000 (admin/admin)"; \
		echo "InfluxDB: http://$$HOST_IP:8086 (admin/adminpassword)"; \
		echo "MQTT: $$HOST_IP:1883"; \
		echo "Meter 001 : 10.28.10.181"; \
		echo "Meter 002 : 10.28.10.182"; \
	else \
		echo "Grafana: http://localhost:3000 (admin/admin)"; \
		echo "InfluxDB: http://localhost:8086 (admin/adminpassword)"; \
	fi

# Stop and clean up everything
stop: ## Stop and clean up all containers, networks, volumes, and .env
	@echo "=== Stopping and cleaning up I2M2G Two-Meter ==="
	@docker compose down -vv
	@docker kill meter_001 2>/dev/null || true
	@docker kill meter_002 2>/dev/null || true
	@docker network prune -f
	@docker system prune -f
	@if [ -f ".env" ]; then \
		echo "Removing .env file..."; \
		rm -f .env; \
	else \
		echo "No .env file found, skipping removal."; \
	fi
	@echo "Complete cleanup finished"

# Pause services (stop containers but keep data)
pause: ## Pause services - stop containers but preserve all data
	@echo "=== Pausing I2M2G Two-Meter Services ==="
	@docker compose down
	@echo "Services paused. Data is preserved."
	@echo "Run 'make resume' to restart services."

# Resume services (start containers with existing data)
resume: ## Resume services - start containers with existing data
	@echo "=== Resuming I2M2G Two-Meter Services ==="
	@docker compose --profile real_meter up -d
	@echo "Services resumed successfully"
	@if [ -f ".env" ]; then \
		HOST_IP=$$(grep METER_IP .env | cut -d'=' -f2 | head -1); \
		echo "Grafana: http://$$HOST_IP:3000 (admin/admin)"; \
		echo "InfluxDB: http://$$HOST_IP:8086"; \
		echo "MQTT: $$HOST_IP:1883"; \
		echo "Meter 001 (Main House): 10.28.10.181"; \
		echo "Meter 002 (Garage): 10.28.10.182"; \
	else \
		echo "Grafana: http://localhost:3000 (admin/admin)"; \
		echo "InfluxDB: http://localhost:8086"; \
		echo "MQTT: localhost:1883"; \
	fi

# Restart the stack (stop + start)
restart: stop start ## Restart the complete stack

# Check SSL keys
check-keys: ## Check if SSL keys exist
	@echo "=== Checking SSL Keys ==="
	@./scripts/generate_keys.sh -p || echo "No SSL keys found. Run 'make generate-keys' to create them."

# Generate SSL keys
generate-keys: ## Generate SSL keys for meter authentication
	@echo "=== Generating SSL Keys ==="
	@chmod +x scripts/generate_keys.sh
	@./scripts/generate_keys.sh
	@echo "SSL keys generated successfully"

# Show status of containers
status: ## Show status of all containers
	@echo "=== Container Status ==="
	@docker compose ps
	@echo ""
	@echo "=== Volume Status ==="
	@docker volume ls
	@echo ""
	@echo "=== Network Status ==="
	@docker network ls | grep i2m2g

# Show logs for all services
logs: ## Show logs for all services
	@echo "=== All Services Logs ==="
	@docker compose logs -f

# Show logs for specific services
logs-mqtt: ## Show MQTT broker logs
	@echo "=== MQTT Broker Logs ==="
	@docker logs -f mosquitto

logs-meter-001: ## Show Meter 001 (Main House) logs
	@echo "=== Meter 001 (Main House) Logs ==="
	@docker logs -f meter_001

logs-meter-002: ## Show Meter 002 (Garage) logs
	@echo "=== Meter 002 (Garage) Logs ==="
	@docker logs -f meter_002

logs-influx: ## Show InfluxDB logs
	@echo "=== InfluxDB Logs ==="
	@docker logs -f influxdb

logs-telegraf: ## Show Telegraf logs
	@echo "=== Telegraf Logs ==="
	@docker logs -f telegraf

logs-grafana: ## Show Grafana logs
	@echo "=== Grafana Logs ==="
	@docker logs -f grafana

# Monitor data flow
monitor: ## Monitor the complete data flow
	@echo "=== Monitoring Two-Meter Data Flow ==="
	@echo "Checking container status..."
	@docker compose ps
	@echo ""
	@echo "Checking SSL keys..."
	@./scripts/generate_keys.sh -p || echo "SSL keys not found"
	@echo ""
	@echo "Checking MQTT connectivity..."
	@docker exec mosquitto mosquitto_pub -h localhost -t test -m "test" 2>/dev/null && echo "MQTT is working" || echo "MQTT connection failed"
	@echo ""
	@echo "Checking InfluxDB connectivity..."
	@curl -s http://localhost:8086/health > /dev/null && echo "InfluxDB is accessible" || echo "InfluxDB connection failed"
	@echo ""
	@echo "Checking Grafana accessibility..."
	@curl -s http://localhost:3000 > /dev/null && echo "Grafana is accessible" || echo "Grafana connection failed"
	@echo ""
	@echo "Checking meter connectivity..."
	@echo "Meter 001 (Main House): 10.28.10.181"
	@echo "Meter 002 (Garage): 10.28.10.182"

# Connect InfluxDB to Grafana automatically and create dashboard
connect-grafana: ## Automatically connect InfluxDB to Grafana and create two-meter dashboard
	@echo "=== Connecting InfluxDB to Grafana ==="
	@chmod +x scripts/connect-grafana.sh
	@./scripts/connect-grafana.sh

# Clean up everything (including volumes)
clean: ## Complete cleanup - removes all containers, networks, volumes, and .env
	@echo "=== Complete Cleanup ==="
	@echo "This will remove ALL data including InfluxDB data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker compose down -v
	@docker kill meter_001 2>/dev/null || true
	@docker kill meter_002 2>/dev/null || true
	@docker volume prune -f
	@docker network prune -f
	@docker system prune -f
	@rm -f .env
	@echo "Complete cleanup finished"

# Quick status check
check: ## Quick health check of the stack
	@echo "=== Quick Health Check ==="
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | grep -E "(mosquitto|meter_001|meter_002|influxdb|telegraf|grafana)" || echo "No containers found"

# Show environment info
env-info: ## Show current environment configuration
	@echo "=== Environment Information ==="
	@if [ -f ".env" ]; then \
		echo ".env file exists"; \
		echo "Environment variables:"; \
		grep -E "^(METER_|MQTT_|INFLUXDB_|GRAFANA_)" .env || echo "No relevant env vars found"; \
	else \
		echo ".env file not found"; \
	fi

# Build images without starting
build: ## Build Docker images without starting containers
	@echo "=== Building Docker Images ==="
	@docker compose --profile real_meter build

# Show recent logs for troubleshooting
troubleshoot: ## Show recent logs for troubleshooting
	@echo "=== Troubleshooting Information ==="
	@echo "Recent Meter 001 logs:"
	@docker logs --tail 10 meter_001 2>/dev/null || echo "meter_001 container not found"
	@echo ""
	@echo "Recent Meter 002 logs:"
	@docker logs --tail 10 meter_002 2>/dev/null || echo "meter_002 container not found"
	@echo ""
	@echo "Recent telegraf logs:"
	@docker logs --tail 10 telegraf 2>/dev/null || echo "telegraf container not found"
	@echo ""
	@echo "Recent influxdb logs:"
	@docker logs --tail 10 influxdb 2>/dev/null || echo "influxdb container not found"
	@echo ""
	@echo "SSL keys status:"
	@./scripts/generate_keys.sh -p 2>/dev/null || echo "SSL keys not found" 