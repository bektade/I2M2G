# I2M2G Makefile - Streamlined project management
# Usage: make <target>

# Detect OS and set appropriate variables
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
    PLATFORM := mac
    START_SCRIPT := start-mac.sh
else
    PLATFORM := linux
    START_SCRIPT := start-linux.sh
endif

# Default target
.DEFAULT_GOAL := help

.PHONY: help setup start stop restart status logs clean logs-mqtt logs-influx logs-grafana logs-telegraf monitor connect-grafana pause resume

# Show help
help: ## Show this help message
	@echo "=== Help Menu for Meter Simulator : ==="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "Platform detected: $(PLATFORM)"
	@echo "Start script: $(START_SCRIPT)"
	@echo ""

GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

# Setup environment and start the stack
setup: ## Setup environment and start the complete stack
	@echo "$(YELLOW)=== Setting up .env and Starting Services on $(PLATFORM) ===$(NC)"
	@chmod +x $(START_SCRIPT)
	@./$(START_SCRIPT)




log: ## Show  meter service logs
	@docker logs -f meter2mqtt



# Stop and clean up everything
stop: ## Stop and clean up all containers, networks, volumes, and .env
	@echo "=== Stopping and cleaning up I2M2G ==="
	@chmod +x stop.sh
	@./stop.sh

# Pause services (stop containers but keep data)
pause: ## Pause services - stop containers but preserve all data
	@echo "=== Pausing I2M2G Services ==="
	@docker compose down
	@echo "Services paused. Data is preserved."
	@echo "Run 'make resume' to restart services."

# Resume services (start containers with existing data)
resume: ## Resume services - start containers with existing data
	@echo "=== Resuming I2M2G Services ==="
	@docker compose up -d
	@echo "Services resumed successfully"
	@if [ -f ".env" ]; then \
		HOST_IP=$$(grep SIMULATOR_IP .env | cut -d'=' -f2); \
		echo "Grafana: http://$$HOST_IP:3000 (admin/admin)"; \
		echo "InfluxDB: http://$$HOST_IP:8086"; \
		echo "MQTT: $$HOST_IP:1883"; \
	else \
		echo "Grafana: http://localhost:3000 (admin/admin)"; \
		echo "InfluxDB: http://localhost:8086"; \
		echo "MQTT: localhost:1883"; \
	fi

# Restart the stack (stop + start)
restart: stop start ## Restart the complete stack

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

logs-meter: ## Show meter2mqtt service logs
	@echo "=== Meter2MQTT Service Logs ==="
	@docker logs -f meter2mqtt

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
	@echo "=== Monitoring Data Flow ==="
	@echo "Checking container status..."
	@docker compose ps
	@echo ""
	@echo "Checking MQTT connectivity..."
	@docker exec mosquitto mosquitto_pub -h localhost -t test -m "test" 2>/dev/null && echo "MQTT is working" || echo "MQTT connection failed"
	@echo ""
	@echo "Checking InfluxDB connectivity..."
	@curl -s http://localhost:8086/health > /dev/null && echo "InfluxDB is accessible" || echo "InfluxDB connection failed"
	@echo ""
	@echo "Checking Grafana accessibility..."
	@curl -s http://localhost:3000 > /dev/null && echo "Grafana is accessible" || echo "Grafana connection failed"

# Connect InfluxDB to Grafana automatically and create dashboard
connect-grafana: ## Automatically connect InfluxDB to Grafana and create power usage dashboard
	@echo "=== Connecting InfluxDB to Grafana ==="
	@chmod +x scripts/connect-grafana.sh
	@./scripts/connect-grafana.sh

# Clean up everything (including volumes)
clean: ## Complete cleanup - removes all containers, networks, volumes, and .env
	@echo "=== Complete Cleanup ==="
	@echo "This will remove ALL data including InfluxDB data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@docker compose down -v
	@docker volume prune -f
	@docker network prune -f
	@docker system prune -f
	@rm -f .env
	@echo ""
	@echo "	✅ cleanup Completed"

# Quick status check
check: ## Quick health check of the stack
	@echo "=== Quick Health Check ==="
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | grep -E "(mosquitto|meter2mqtt|influxdb|telegraf|grafana)" || echo "No containers found"

# Show environment info
env-info: ## Show current environment configuration
	@echo "=== Environment Information ==="
	@if [ -f ".env" ]; then \
		echo ".env file exists"; \
		echo "Environment variables:"; \
		grep -E "^(SIMULATOR_IP|MQTT_|INFLUXDB_|GRAFANA_)" .env || echo "No relevant env vars found"; \
	else \
		echo ".env file not found"; \
	fi

# Build images without starting
build: ## Build Docker images without starting containers
	@echo "=== Building Docker Images ==="
	@docker compose build

# Show recent logs for troubleshooting
troubleshoot: ## Show recent logs for troubleshooting
	@echo "=== Troubleshooting Information ==="
	@echo "Recent meter2mqtt logs:"
	@docker logs --tail 10 meter2mqtt 2>/dev/null || echo "meter2mqtt container not found"
	@echo ""
	@echo "Recent telegraf logs:"
	@docker logs --tail 10 telegraf 2>/dev/null || echo "telegraf container not found"
	@echo ""
	@echo "Recent influxdb logs:"
	@docker logs --tail 10 influxdb 2>/dev/null || echo "influxdb container not found" 