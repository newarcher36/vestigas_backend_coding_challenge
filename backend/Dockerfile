FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application code into a proper Python package path
COPY . /app/backend

# Run the service via the package path
CMD ["/app/backend/start.sh"]
