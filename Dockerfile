FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY app/ModelForge-1/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ModelForge-1 application code
COPY app/ModelForge-1/ ./app/ModelForge-1/

# Create necessary directories
RUN mkdir -p app/ModelForge-1/uploads app/ModelForge-1/generated

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app

# Run the ModelForge-1 application
CMD ["python", "app/ModelForge-1/app.py"]