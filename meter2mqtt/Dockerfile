FROM python:3.10-slim

# Set working directory
WORKDIR /opt/meter2mqtt

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variable for SSL configuration if needed
ENV OPENSSL_CONF=/opt/meter2mqtt/openssl.conf

# Create necessary directories
RUN mkdir -p /opt/meter2mqtt/certs /opt/meter2mqtt/configs

# Set the entry point
CMD ["python", "main.py"] 