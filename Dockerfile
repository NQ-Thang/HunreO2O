FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=10000 \
    APP_ENV=production

EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail --silent "http://127.0.0.1:${PORT}/up" > /dev/null || exit 1

# Start the unified server
CMD ["sh", "-c", "cd /app/BTL/services && uvicorn local_api_server:app --host 0.0.0.0 --port ${PORT:-10000}"]
