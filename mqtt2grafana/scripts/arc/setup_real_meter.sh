#!/bin/bash

# Setup script for real meter configuration
echo "Setting up environment for REAL METER..."
echo "This configuration requires SSL certificates and mDNS discovery"
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

# Copy the real meter template
cp env.template.real_meter .env

echo "Real meter environment template copied to .env"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your specific meter IP and certificate paths"
echo "2. Ensure your SSL certificates are in the certs/ directory"
echo "3. Run: docker compose --profile real_meter up"
echo ""
echo "Configuration file created: .env" 