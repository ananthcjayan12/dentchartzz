FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create static and media directories
RUN mkdir -p /app/static /app/media

# Copy project
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Run the application
ENTRYPOINT ["/app/entrypoint.sh"] 