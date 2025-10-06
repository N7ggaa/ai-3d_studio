FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for all Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgtk-3-0 \
    libgomp1 \
    libgthread-2.0-0 \
    libgl1-mesa-glx \
    libegl1-mesa \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY app/ModelForge-1/requirements.txt ./requirements.txt

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir --verbose -r requirements.txt

# Copy the ModelForge-1 application code to root for proper imports
# Copy everything except requirements.txt first (it will be overwritten)
COPY app/ModelForge-1/ ./
# Then copy requirements.txt again to ensure it's in place
COPY app/ModelForge-1/requirements.txt ./requirements.txt

# Create necessary directories
RUN mkdir -p uploads generated instance

# Expose port 5000
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "app.py"]