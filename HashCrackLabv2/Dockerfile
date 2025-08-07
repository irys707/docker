FROM python:3.11-slim

# --- Install hashcat + gosu BEFORE creating appuser
USER root

RUN apt-get update && apt-get install -y \
    hashcat \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create appuser (non-root)
RUN useradd -m appuser

# Set working directory
WORKDIR /app

# Copy source code
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy secure entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use custom entrypoint
ENTRYPOINT ["/entrypoint.sh"]
