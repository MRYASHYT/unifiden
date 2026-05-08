# Use a slim Python 3.11 image
FROM python:3.11-slim

# Set environment variables for security and performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (for DuckDuckGo Search and Cryptography)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create keys and data directories with proper permissions
RUN mkdir -p security/keys data results paper/figures \
    && chmod -R 700 security/keys \
    && chmod -R 755 data results paper/figures

# Expose no ports by default for air-gapped security
# Run as non-root user for extra security
RUN useradd -m agentuser
USER agentuser

# Default command: run the pilot
ENTRYPOINT ["python", "main.py"]
CMD ["--mode", "pilot"]
