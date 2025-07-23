#!/bin/bash

# Setup script for simulator configuration
echo "Setting up environment for SIMULATOR..."
echo "This configuration is simple - no SSL certificates required"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "Warning: .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Copy the simulator template
cp env.template.simulator .env

echo "Simulator environment template copied to .env"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your simulator host IP (if not localhost)"
echo "2. Ensure the meter simulator is running on port 8082"
echo "3. Run: docker compose --profile simulator up"
echo ""
echo "Configuration file created: .env" 