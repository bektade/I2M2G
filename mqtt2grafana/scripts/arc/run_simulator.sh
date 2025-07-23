#!/bin/bash

# Run the simulator version of the Xcel meter integration
echo "Starting Xcel Simulator Integration..."
echo "This will connect to the meter simulator and publish data to MQTT"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please run setup_simulator.sh first to create the .env file."
    echo ""
    echo "To setup simulator configuration:"
    echo "  ./setup_simulator.sh"
    exit 1
fi

# Run with simulator profile
docker compose --profile simulator up 