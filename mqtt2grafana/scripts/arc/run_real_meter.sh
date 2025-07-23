#!/bin/bash

# Run the real meter version of the Xcel meter integration
echo "Starting Xcel Real Meter Integration..."
echo "This will connect to a real Xcel Energy smart meter"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please run setup_real_meter.sh first to create the .env file."
    echo ""
    echo "To setup real meter configuration:"
    echo "  ./setup_real_meter.sh"
    exit 1
fi

# Check if certificates exist
if [ ! -f certs/.cert.pem ] || [ ! -f certs/.key.pem ]; then
    echo "Warning: SSL certificates not found in certs/ directory!"
    echo "Please ensure your certificates are properly configured."
    echo ""
fi

# Run with real meter profile
docker compose --profile real_meter up 